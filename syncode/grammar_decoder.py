import copy
import time
import torch
import common
from transformers import LogitsProcessor, PreTrainedTokenizer
from parsers.incremental_parser import IncrementalParser, ParseResult
from parsers import create_parser
from dfa_mask_store import DFAMaskStore
from parsers.grammars.grammar import Grammar


class GrammarDecoder(LogitsProcessor):
    """
    This class is used to filter the logits of the model to only allow syntactically valid tokens for Python. 

    Args:
        grammar (str): The grammar to use for parsing e.g. "python".
        tokenizer (PreTrainedTokenizer): The tokenizer to use for decoding.
        logger (common.Logger): The logger to use for logging.
        use_cache (bool, optional): Whether to use the cache. Defaults to True.
        parse_prompt (bool, optional): Whether to parse the prompt. Defaults to True.
        dev_mode (bool, optional): Whether to run in development mode. Defaults to False.
    """
    def __init__(self, 
        grammar: Grammar, 
        tokenizer: PreTrainedTokenizer, 
        logger: common.Logger, 
        use_cache=True,
        parse_prompt=True, 
        num_samples=1,
        dev_mode=False,
        parser='lalr',
        **kwargs):

        time_start = time.time()
        self.tokenizer = tokenizer
        self.grammar = grammar
        self.logger = logger
        self.dev_mode = dev_mode
        self.batch_size = num_samples
        self.inc_parsers: list[IncrementalParser] = []

        # For backtracking to syntactically valid completions
        self.partial_codes_trace: list = []
        self.last_valid_state: list = []
        self.function_end: list = []

        # We use this when only the LLM output is parsed and not (input+output)
        self.parse_prompt = parse_prompt
        self.start_from = None         

        # Load dfa mask store
        self.dfa_mask_store = DFAMaskStore.load_dfa_mask_store(
                                    grammar=self.grammar, 
                                    tokenizer=self.tokenizer, 
                                    use_cache=use_cache, 
                                    logger=self.logger
                                    )

        # Create parsers
        self.inc_parsers = [create_parser(self.grammar, logger=self.logger, parser=parser) for _ in range(self.batch_size)]

        # For profiling
        self.token_cnt = 0
        self.debug = True
        self.logger.log_time(f"Time taken for preprocessing: {time.time() - time_start:.2f}s")
        
    def _log_current_status(self, partial_code, r: ParseResult):
        self.logger.log_code('Partial code', partial_code)
        self.logger.log(repr(r))

    def reset(self):
        """
        Resets the decoder state on every new prompt.
        """
        self.last_valid_state = [0 for _ in range(self.batch_size)]
        self.function_end = [None for _ in range(self.batch_size)]
        self.partial_codes_trace = []
        self.token_cnt = 0
        self.start_from = None 
        for p in self.inc_parsers:
            p.reset()


    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:    
        time1 = time.time() 
        # start_from is used for choosing where the parsing should start
        if self.start_from == None:
            if self.parse_prompt:
                self.start_from = 0
            else:
                self.start_from = len(input_ids[0])
                
        partial_codes = self.tokenizer.batch_decode(input_ids[:, self.start_from:], skip_special_tokens=True)

        self.token_cnt += self.batch_size
        greedy_grammar_token = None
        for i, partial_code in enumerate(partial_codes):
            try:
                time2 = time.time()
                self.partial_codes_trace.append(partial_code)

                # returns the names of the Terminals that are currently accepted.
                r = self.inc_parsers[i].get_acceptable_next_terminals(partial_code)
                self.logger.log_time(f"Time taken for compilation: {time.time() - time2:.3f}s")

                self.update_valid_state(input_ids, i, r)
            
                accept_mask = self.dfa_mask_store.get_overapprox_tokens_mask(r, logger=self.logger)

                if self.debug:
                    self._log_current_status(partial_code, r)
                greedy_token = self.tokenizer.decode(scores[i].argmax(dim=-1)) # For debugging, do not move this line

                if torch.sum(accept_mask) != 0: # If there are acceptable tokens for the current partial code 
                    if len(scores[i]) != len(accept_mask):
                        # Pad accept_mask with 0 values. Since scores[i] may be longer than tokenizer vocab size, we need to pad accept_mask with 0 values
                        accept_mask = torch.cat((accept_mask, torch.zeros(len(scores[i]) - len(accept_mask), dtype=torch.bool)))
                        
                    scores[i] = scores[i].masked_fill(~accept_mask.to(scores.device), -float("inf"))
                else: # Otherwise, report the error and mask no tokens
                    self.logger.log('No acceptable tokens for the current partial code!')
                    self._log_current_status(partial_code, r)

                self.logger.log_time(f"Time taken for masking: {time.time() - time2:.3f}s")
                
                # For debugging - remove later
                greedy_grammar_token = self.tokenizer.decode(scores[i].argmax(dim=-1))
                if greedy_token != greedy_grammar_token:
                    self._log_greedy_difference(greedy_grammar_token, partial_code, r, greedy_token)
            except Exception as e:
                if self.dev_mode == True:
                    raise e
                self.logger.log(f"Exception: {e}")

        self.logger.log_time(f"Time taken for decoding: {time.time() - time1:.3f}s")
        return scores

    def update_valid_state(self, input_ids, i: int, r: ParseResult):
        """
        This a simple heuristic to cut off the generated output at the end of the function. 
        TODO: Put this under a flag to enable/disable this heuristic.
        """
        for accept_seq in r.accept_sequences:
            if accept_seq[0] == '$EOC' and self.function_end[i]==None:
                self.function_end[i] = len(input_ids[i])
            
            # 'EOF' is special terminal since $END does not work with pythong
            if accept_seq[0] == '$END' or accept_seq[0] == 'EOF':
                self.last_valid_state[i] = len(input_ids[i])-1

    def _log_greedy_difference(self, greedy_grammar_token, partial_code, r, greedy_token):
        self.logger.log_check(f"Greedy token and greedy grammar-based token do not match!")
        self.logger.log(f"Greedy token: {repr(greedy_token)}")
        self.logger.log(f"Greedy grammar-based token: {repr(greedy_grammar_token)}")
        self._log_current_status(partial_code, r)
    