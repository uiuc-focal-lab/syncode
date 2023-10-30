import time
import torch
import common
from transformers import LogitsProcessor, PreTrainedTokenizer
from incremental_parser import IncrementalParser


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
        self.partial_codes = []
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

    def _reset(self):
        self.inc_parsers = [IncrementalParser() for _ in range(self.batch_size)]

        self.accept_tokens_sizes = []
        self.partial_codes = []
        self.last_valid_stage = 0
        self.token_cnt = 0
        
        

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:
        partial_codes = self.tokenizer.batch_decode(input_ids, skip_special_tokens=True)

        if self.batch_size == None or (len(self.partial_codes) > 0 and self.partial_codes[-1] not in partial_codes[0]):
            self.batch_size = len(partial_codes)
            self._reset()

        self.token_cnt += self.batch_size
        greedy_grammar_token = None

        for i, partial_code in enumerate(partial_codes):
            try:
                compilation_start_time = time.time()
                self.partial_codes.append(partial_code)

                # returns the names of the Terminals that are currently accepted.
                cur_ac_terminals, next_ac_terminals, incomplete_terminal = self.inc_parsers[i].get_acceptable_next_terminals(partial_code)

                greedy_token = self.tokenizer.decode(scores.argmax(dim=-1), skip_special_tokens=True) # For debugging - remove later

                if 'EOF' in next_ac_terminals:
                    self.last_valid_stage = len(input_ids[0])

                self.accept_tokens_sizes.append(len(cur_ac_terminals))  # For profiling

                accept_mask = self.terminals_nfa.get_overapprox_tokens_mask(incomplete_terminal, next_ac_terminals)

                print('partial code:\n', repr(partial_code))
                print('inc:', repr(incomplete_terminal), '\n', 'cur:', cur_ac_terminals, '\n', 'next:', next_ac_terminals)

                scores[i] = scores[i].masked_fill(~accept_mask.to(scores.device), -float("inf"))

                if self.debug and self.token_cnt%50==0:
                    print('Time taken for compilation:', time.time() - compilation_start_time)

                greedy_grammar_token = self.tokenizer.decode(scores.argmax(dim=-1), skip_special_tokens=True)

                if greedy_token != greedy_grammar_token:
                    print('Greedy token:', repr(greedy_token), scores.argmax(dim=-1))
                    print('Greedy grammar-based token:', repr(greedy_grammar_token), scores.argmax(dim=-1))
                    print('Current acceptable terminals:', cur_ac_terminals)
                    print('Next acceptable terminals:', next_ac_terminals) 
                    print('Partial code:', partial_code)
                    self.non_matching_token_cnt += 1
            except Exception as e:
                print("-"*80, '\n', 'Code lenght:', len(partial_code), '\n', partial_code, '\n', repr(partial_code), '\n', 'Error:', e)

        return scores
    