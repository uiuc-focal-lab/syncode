import time
import torch
import common
from transformers import LogitsProcessor, PreTrainedTokenizer
from incremental_parser import ParseResult
from grammars.python_parser import PythonIncrementalParser


class PythonDecoder(LogitsProcessor):
    """
    This class is used to filter the logits of the model to only allow syntactically valid tokens for Python. 
    """
    def __init__(self, tokenizer: PreTrainedTokenizer, **kwargs):
        time_start = time.time()
        self.tokenizer = tokenizer

        self.batch_size = None # We update this in the first call to __call__
        self.inc_parsers = None
        
        # For backtracking to syntactically valid completions
        self.partial_codes_trace = []
        self.last_valid_stage = 0

        # For profiling
        self.token_cnt = 0
        self.accept_tokens_sizes = []
        self.non_matching_token_cnt = 0

        # Load NFA
        self.terminals_nfa = common.load_nfa(tokenizer=self.tokenizer, use_cache=True)

        self.start_time = time.time()
        self.prev_time = self.start_time
        self.debug = True
            
        print(f"Time taken for preprocessing: {time.time() - time_start:.2f}s")

    def _print_current_status(self, partial_code, r: ParseResult):
        print('partial code:\n', repr(partial_code))
        print('inc:', repr(r.remainder), '\n', 'cur:', r.cur_accept_terminals, '\n', 'next:', r.next_accept_terminals)


    def _reset(self):
        self.inc_parsers = [PythonIncrementalParser() for _ in range(self.batch_size)]
        self.last_valid_state = [0 for _ in range(self.batch_size)]
        self.accept_tokens_sizes = []
        self.partial_codes_trace = []
        self.token_cnt = 0
        

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:
        partial_codes = self.tokenizer.batch_decode(input_ids, skip_special_tokens=True)

        if self.batch_size == None or (len(self.partial_codes_trace) > 0 and self.partial_codes_trace[0] not in partial_codes[0]):
            self.batch_size = len(partial_codes)
            self._reset()

        self.token_cnt += self.batch_size
        greedy_grammar_token = None

        for i, partial_code in enumerate(partial_codes):
            try:
                compilation_start_time = time.time()
                self.partial_codes_trace.append(partial_code)

                # returns the names of the Terminals that are currently accepted.
                r = self.inc_parsers[i].get_acceptable_next_terminals(partial_code)

                greedy_token = self.tokenizer.decode(scores[i].argmax(dim=-1), skip_special_tokens=True) # For debugging - remove later

                if 'EOF' in r.next_accept_terminals:
                    self.last_valid_state[i] = len(input_ids[i])

                self.accept_tokens_sizes.append(len(r.cur_accept_terminals))  # For profiling

                print(i, 'Time taken for compilation:', time.time() - compilation_start_time)
                accept_mask = self.terminals_nfa.get_overapprox_tokens_mask(r)

                print(i, 'Time taken for overapproximation:', time.time() - compilation_start_time)
                if self.debug:
                    # print(scores[i][:20])
                    self._print_current_status(partial_code, r)
                
                if torch.sum(accept_mask) != 0: # If there are acceptable tokens for the current partial code 
                    scores[i] = scores[i].masked_fill(~accept_mask.to(scores.device), -float("inf"))
                else: # Otherwise, report the error and mask no tokens
                    print('No acceptable tokens for the current partial code!')
                    self._print_current_status(partial_code, r)

                print(i, 'Time taken for masking:', time.time() - compilation_start_time)  

                greedy_grammar_token = self.tokenizer.decode(scores[i].argmax(dim=-1), skip_special_tokens=True)

                if greedy_token != greedy_grammar_token:
                    print('Greedy token:', repr(greedy_token))
                    print('Greedy grammar-based token:', repr(greedy_grammar_token))
                    self._print_current_status(partial_code, r)
                    self.non_matching_token_cnt += 1
            except Exception as e:
                print("-"*80, '\n', 'Code lenght:', len(partial_code), '\n', partial_code, '\n', repr(partial_code), '\n', 'Error:', e)

        return scores
    