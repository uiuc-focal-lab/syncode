import time
import torch
import common
from transformers import LogitsProcessor, PreTrainedTokenizer
from incremental_parser import ParseResult
from grammars.python_parser import PythonIncrementalParser


class GrammarDecoder(LogitsProcessor):
    """
    This class is used to filter the logits of the model to only allow syntactically valid tokens for Python. 

    Args:
        grammar (str): The grammar to use for parsing e.g. "python".
        tokenizer (PreTrainedTokenizer): The tokenizer to use for decoding.
        logger (common.Logger): The logger to use for logging.
        use_cache (bool, optional): Whether to use the cache. Defaults to True.
        parse_prompt (bool, optional): Whether to parse the prompt. Defaults to True.
    """
    def __init__(self, 
        grammar: str, 
        tokenizer: PreTrainedTokenizer, 
        logger: common.Logger, 
        use_cache=True,
        parse_prompt=True, 
        **kwargs):

        time_start = time.time()
        self.tokenizer = tokenizer
        self.grammar = grammar
        self.logger = logger

        self.batch_size = -1 # We update this in the first call to __call__
        self.inc_parsers: list = []

        # For backtracking to syntactically valid completions
        self.partial_codes_trace: list = []
        self.last_valid_state: list = []
        self.function_end: list = []

        # We use this when only the LLM output is parsed and not (input+output)
        self.parse_prompt = parse_prompt
        self.start_from = None 

        # For profiling
        self.token_cnt = 0
        self.accept_tokens_sizes: list = []
        self.non_matching_token_cnt = 0

        # Load dfa mask store
        self.dfa_mask_store = common.load_dfa_mask_store(grammar=self.grammar, tokenizer=self.tokenizer, use_cache=use_cache)

        self.start_time = time.time()
        self.prev_time = self.start_time
        self.debug = True
        self.logger.log(f"Time taken for preprocessing: {time.time() - time_start:.2f}s")


    def _log_current_status(self, partial_code, r: ParseResult):
        self.logger.log_code('Partial code', partial_code)
        self.logger.log(repr(r))


    def _reset(self):
        self.inc_parsers = [common.create_parser(self.grammar) for _ in range(self.batch_size)]
        self.last_valid_state = [0 for _ in range(self.batch_size)]
        self.function_end = [None for _ in range(self.batch_size)]
        self.accept_tokens_sizes = []
        self.partial_codes_trace = []
        self.token_cnt = 0
        self.start_from = None 
        

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:
        
        # start_from is used for choosing where the parsing should start
        if self.start_from == None:
            if self.parse_prompt:
                self.start_from = 0
            else:
                self.start_from = len(input_ids[0])
                
        partial_codes = self.tokenizer.batch_decode(input_ids[:, self.start_from:], skip_special_tokens=True)

        if self.batch_size == -1 or (len(self.partial_codes_trace) > 0 and self.partial_codes_trace[0] not in partial_codes[0]):
            self.batch_size = len(input_ids)
            self._reset()

        self.token_cnt += self.batch_size
        greedy_grammar_token = None
        for i, partial_code in enumerate(partial_codes):
            try:
                compilation_start_time = time.time()
                self.partial_codes_trace.append(partial_code)

                # returns the names of the Terminals that are currently accepted.
                r = self.inc_parsers[i].get_acceptable_next_terminals(partial_code)
                
                greedy_token = self.tokenizer.decode(scores[i].argmax(dim=-1)) # For debugging - remove later
                if '$END' in r.next_accept_terminals:
                    self.last_valid_state[i] = len(input_ids[i])
                if 'EOC' in r.next_accept_terminals and self.function_end[i]==None:
                    self.function_end[i] = len(input_ids[i])

                self.accept_tokens_sizes.append(len(r.cur_accept_terminals))  # For profiling
                self.logger.log(f"Time taken for compilation: {time.time() - compilation_start_time:.2f}s")
                accept_mask = self.dfa_mask_store.get_overapprox_tokens_mask(r)
                self.logger.log(f"Time taken for overapproximation: {time.time() - compilation_start_time:.2f}s")

                if self.debug:
                    self._log_current_status(partial_code, r)
                
                if torch.sum(accept_mask) != 0: # If there are acceptable tokens for the current partial code 
                    if len(scores[i]) != len(accept_mask):
                        # Pad accept_mask with 0 values. Since scores[i] may be longer than tokenizer vocab size, we need to pad accept_mask with 0 values
                        accept_mask = torch.cat((accept_mask, torch.zeros(len(scores[i]) - len(accept_mask), dtype=torch.bool)))
                        
                    scores[i] = scores[i].masked_fill(~accept_mask.to(scores.device), -float("inf"))
                else: # Otherwise, report the error and mask no tokens
                    self.logger.log('No acceptable tokens for the current partial code!')
                    self._log_current_status(partial_code, r)

                self.logger.log(f"Time taken for masking: {time.time() - compilation_start_time:.2f}s")
                
                greedy_grammar_token = self.tokenizer.decode(scores[i].argmax(dim=-1))

                if greedy_token != greedy_grammar_token:
                    self.logger.log(f"Greedy token: {repr(greedy_token)}")
                    self.logger.log(f"Greedy grammar-based token: {repr(greedy_grammar_token)}")
                    self._log_current_status(partial_code, r)
                    self.non_matching_token_cnt += 1
            except Exception as e:
                self.logger.log(f"Exception: {e}")

        return scores
    