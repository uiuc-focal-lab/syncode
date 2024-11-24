from typing import Iterator
import torch
import syncode.common as common
from transformers import LogitsProcessor, PreTrainedTokenizer
from syncode.parse_result import AcceptSequence, RemainderState
from syncode.parsers.incremental_parser import IncrementalParser, ParseResult
from syncode.parsers import create_parser, create_base_parser
from syncode.dfa_mask_store import DFAMaskStore
from syncode.parsers.grammars import Grammar


class SyncodeLogitsProcessor(LogitsProcessor):
    """
    This class is used to filter the logits of the model to only allow syntactically valid tokens for Python. 

    Args:
        grammar (str): The grammar to use for parsing e.g. "python".
        tokenizer (PreTrainedTokenizer): The tokenizer to use for decoding.
        logger (common.Logger): The logger to use for logging.
        use_cache (bool, optional): Whether to use the cache. Defaults to True.
        parse_output_only (bool, optional): Whether to parse the prompt. Defaults to False.
        dev_mode (bool, optional): Whether to run in development mode. Defaults to False.
    """
    def __init__(self, 
        grammar: Grammar, 
        tokenizer: PreTrainedTokenizer, 
        logger: common.Logger=common.EmptyLogger(), 
        use_cache=True,
        parse_output_only=False, 
        num_samples=1,
        dev_mode=False,
        parser='lalr',
        mode='grammar_mask'):

        self.tokenizer = tokenizer
        self.grammar = grammar
        self.logger = logger
        self.dev_mode = dev_mode
        self.batch_size = num_samples

        # For backtracking to syntactically valid completions
        self.last_valid_state: list = []
        self.function_end: list = []

        # We use this when only the LLM output is parsed and not (input+output)
        self.parse_output_only = parse_output_only
        self.start_from = None         

        # Ignore whitespace tokens
        self._ignore_whitespace = self._get_ignore_whitespace(self.grammar)

        # Load dfa mask store
        self.dfa_mask_store = DFAMaskStore.load_dfa_mask_store(
                                    grammar=self.grammar, 
                                    tokenizer=self.tokenizer, 
                                    use_cache=use_cache, 
                                    logger=self.logger,
                                    mode=mode,
                                    )

        # Create parsers
        self.inc_parser: Iterator[IncrementalParser] = create_parser(self.grammar, logger=self.logger, parser=parser, ignore_whitespace=self._ignore_whitespace)

    
    def _log_current_status(self, partial_code, r: ParseResult):
        self.logger.log_code('Partial code', partial_code)
        self.logger.log(repr(r))

    def _get_ignore_whitespace(self, grammar):
        """
        Check if the grammar allows whitespace tokens to be ignored.
        """
        base_parser = create_base_parser(grammar)
        terminals = base_parser.terminals
        ignore_terminals = base_parser.ignore_tokens
        
        import regex
        ignore_whitespace = False
        for ig_name in ignore_terminals:
            for terminal in terminals:
                if terminal.name == ig_name:
                    if regex.match(terminal.pattern.to_regexp(), ' ') is not None:
                        ignore_whitespace = True # convert to boolean tensor mask. This is useful for fast union operations
        return ignore_whitespace

    def reset(self, prompt: str):
        """
        Resets the decoder state on every new prompt.
        """
        self.last_valid_state = [0 for _ in range(self.batch_size)]
        self.function_end = [None for _ in range(self.batch_size)]

        if (isinstance(prompt, str)):
            prompt_tokens = self.tokenizer.encode(prompt, return_tensors='pt')[0]
        elif (isinstance(prompt, list)):
            prompt_tokens = self.tokenizer.apply_chat_template(
                prompt, 
                add_generation_prompt=True, 
                return_tensors="pt",
                return_dict=True
            )[0]
        
        if self.parse_output_only:
            self.start_from = len(prompt_tokens)
        else:
            self.start_from = 0
        
        self.inc_parser.reset()


    def is_valid(self, input_ids: torch.LongTensor, next_token: torch.LongTensor) -> bool:
        """
        Check if the next token is valid given the input_ids.

        Args:
            input_ids (torch.LongTensor): The input ids.
            next_token (torch.LongTensor): The next token.

        Returns:
            bool: True if the next token is valid, False otherwise.
        """
        assert len(input_ids) == 1, "Only one input is supported for now."
        input_ids = torch.cat((input_ids, next_token.unsqueeze(0)), dim=-1)
        partial_code = self._get_partial_codes(input_ids)[0]

        try:
            r = self.inc_parser.get_acceptable_next_terminals(partial_code)
        except Exception as e:
            self.logger.log(f"Exception while parsing:\n {e}")
            return False
        
        self.update_valid_state(input_ids, 0, r)

        if input_ids[0, -1] == self.tokenizer.eos_token_id:
            return AcceptSequence(['$END']) in r.accept_sequences

        if r.remainder_state == RemainderState.COMPLETE or r.remainder_state == RemainderState.MAYBE_COMPLETE:
            return True

        # Check if the remainder is a valid prefix for the last terminal
        out = self.dfa_mask_store.is_valid_prefix(r)
        return out
    

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:    
        # start_from is used for choosing where the parsing should start
        debug = True
        partial_codes = self._get_partial_codes(input_ids)

        for idx, partial_code in enumerate(partial_codes):
            ## Parsing
            try: # returns the accept sequences that are currently accepted.
                r = self.inc_parser.get_acceptable_next_terminals(partial_code)
            except Exception as e:
                if self.dev_mode == True:
                    raise e
                self.logger.log(f"Exception while parsing:\n {e}")
                continue  # Skip altering the scores for this batch

            self.update_valid_state(input_ids, idx, r)
        
            accept_mask = self.dfa_mask_store.get_accept_mask(r, logger=self.logger)

            if debug: 
                self._log_current_status(partial_code, r)
                greedy_token = self.tokenizer.decode(scores[idx].argmax(dim=-1)) 

            if torch.sum(accept_mask) != 0: # If there are acceptable tokens for the current partial code 
                if len(scores[idx]) != len(accept_mask):
                    # Pad accept_mask with 0 values. Since scores[i] may be longer than tokenizer vocab size, we need to pad accept_mask with 0 values
                    accept_mask = torch.cat((accept_mask, torch.zeros(len(scores[idx]) - len(accept_mask), dtype=torch.bool)))
                    
                scores[idx] = scores[idx].masked_fill(~accept_mask.to(scores.device), -float("inf"))
            else: # Otherwise, report the error and mask no tokens
                self.logger.log('No acceptable tokens for the current partial code!')
                self._log_current_status(partial_code, r)

            # For debugging - remove later
            if debug: self._debug_greedy(scores, idx, partial_code, r, greedy_token)

        return scores

    def _get_partial_codes(self, input_ids: torch.LongTensor):   
        assert self.start_from <= input_ids.size(1), "Make sure that the decoder is reset for new prompt."            
        partial_codes = self.tokenizer.batch_decode(input_ids[:, self.start_from:], skip_special_tokens=True)
        return partial_codes

    def update_valid_state(self, input_ids, idx: int, r: ParseResult):
        """
        This a simple heuristic to cut off the generated output at the end of the function. 
        TODO: Put this under a flag to enable/disable this heuristic.
        """
        if idx < len(self.function_end):
            if r.function_end and self.function_end[idx] == None: # If the function end is not None, then the last valid state is the function end
                self.function_end[idx] = len(input_ids[idx])-1

        if idx < len(self.last_valid_state):
            for accept_seq in r.accept_sequences:
                # 'EOF' is special terminal since $END does not work with python
                if accept_seq[0] == '$END' or accept_seq[0] == 'EOF':
                    self.last_valid_state[idx] = len(input_ids[idx])-1

    def _debug_greedy(self, scores, idx, partial_code, r, greedy_token):
        greedy_grammar_token = self.tokenizer.decode(scores[idx].argmax(dim=-1))
        if greedy_token != greedy_grammar_token:
            self._log_greedy_difference(greedy_grammar_token, partial_code, r, greedy_token)

    def _log_greedy_difference(self, greedy_grammar_token, partial_code, r, greedy_token):
        self.logger.log_check(f"Greedy token and greedy grammar-based token do not match!")
        self.logger.log(f"Greedy token: {repr(greedy_token)}")
        self.logger.log(f"Greedy grammar-based token: {repr(greedy_grammar_token)}")
        self._log_current_status(partial_code, r)
    