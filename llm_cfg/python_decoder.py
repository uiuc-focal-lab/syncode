import time
import torch
import common
from transformers import LogitsProcessor, PreTrainedTokenizer
from incremental_parser import IncrementalParser


class PythonDecoder(LogitsProcessor):
    def __init__(self, tokenizer: PreTrainedTokenizer, **kwargs):
        time_start = time.time()
        self.tokenizer = tokenizer
        self.inc_parser = IncrementalParser()
        
        self.token_cnt = 0
        self.accept_tokens_sizes = []
        self.non_matching_token_cnt = 0
        self.partial_codes = []
        self.last_valid_stage = 0
        self.terminals_nfa = common.load_nfa(tokenizer=self.tokenizer, inc_parser=self.inc_parser, use_cache=True)

        # Iterate through the vocabulary and create a map of (tokenizer token -> grammar terminal)
        # Note: It may happen that many tokens do not fall in any category
        self.terminal_to_mask = {}
        self.uncategorezed_mask = torch.zeros(tokenizer.vocab_size, dtype=torch.bool)

        self.start_time = time.time()
        self.prev_time = self.start_time
        self.debug = True

        for i in range(tokenizer.vocab_size):
            token = tokenizer.decode(torch.tensor([i]), skip_special_tokens=True)
            token_types = []

            token_type = self.inc_parser.get_matching_terminal(token)
            prefix_token_types = self.inc_parser.get_prefix_terminals_match(token)

            token_types.append(token_type)
            token_types += prefix_token_types

            for token_type in token_types:
                if not token_type in self.terminal_to_mask:
                    self.terminal_to_mask[token_type] = torch.zeros(tokenizer.vocab_size, dtype=torch.bool)
                self.terminal_to_mask[token_type][i] = True
        
        print(f"Time taken for preprocessing: {time.time() - time_start:.2f}s")

    def _reset(self):
        self.token_cnt = 0
        self.accept_tokens_sizes = []
        self.partial_codes = []
        self.last_valid_stage = 0
        self.inc_parser = IncrementalParser()
        

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:
        partial_code = self.tokenizer.decode(input_ids[0], skip_special_tokens=True)

        if len(self.partial_codes) > 0 and self.partial_codes[-1] not in partial_code:
            self._reset()

        self.token_cnt += 1
        greedy_grammar_token = None
        try:
            compilation_start_time = time.time()
            self.partial_codes.append(partial_code)

            # returns the names of the Terminals that are currently accepted.
            cur_ac_terminals, next_ac_terminals, incomplete_terminal = self.inc_parser.get_acceptable_next_terminals(partial_code)

            greedy_token = self.tokenizer.decode(scores.argmax(dim=-1), skip_special_tokens=True) # For debugging - remove later

            if 'EOF' in next_ac_terminals:
                self.last_valid_stage = len(input_ids[0])

            self.accept_tokens_sizes.append(len(cur_ac_terminals))  # For profiling

            accept_mask = self.terminals_nfa.get_overapprox_tokens_mask(incomplete_terminal, next_ac_terminals)

            print('partial code:')
            print(repr(partial_code))
            print('inc:', repr(incomplete_terminal))
            print(next_ac_terminals)
            scores = scores.masked_fill(~accept_mask.to(scores.device), -float("inf"))

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
    