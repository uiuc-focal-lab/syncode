import time
import torch
from transformers import LogitsProcessor, PreTrainedTokenizer
from incremental_parser import IncrementalParser


class PythonDecoder(LogitsProcessor):
    def __init__(self, tokenizer: PreTrainedTokenizer, **kwargs):
        self.mask_invalid_tokens = True
        time_start = time.time()
        self.tokenizer = tokenizer
        self.inc_parser = IncrementalParser()
        self.debug = True
        self.token_cnt = 0
        self.accept_tokens_sizes = []
        self.non_matching_token_cnt = 0
        self.partial_codes = []

        # Iterate through the vocabulary and create a map of (tokenizer token -> grammar terminal)
        # Note: It may happen that many tokens do not fall in any category
        self.terminal_to_mask = {}
        self.uncategorezed_mask = torch.zeros(tokenizer.vocab_size, dtype=torch.bool)

        self.start_time = time.time()
        self.prev_time = self.start_time

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
        self.inc_parser = IncrementalParser()

    def _get_next_terminal_mask(self, next_ac_terminals):
        accept_mask = self.uncategorezed_mask.clone()
        # print(accept_mask.sum())

        for token_type in next_ac_terminals:
            if token_type in self.terminal_to_mask:
                accept_mask |= self.terminal_to_mask[token_type]
            # print(accept_mask.sum())
        
        return accept_mask

    def _get_cur_terminal_mask(self, cur_ac_terminals, cur_term_str):
        accept_mask = torch.zeros(self.tokenizer.vocab_size, dtype=torch.bool)
        # TODO: implement this
        return accept_mask    

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:
        partial_code = self.tokenizer.decode(input_ids[0], skip_special_tokens=True)

        if len(self.partial_codes) > 0 and self.partial_codes[-1] not in partial_code:
            self._reset()

        self.token_cnt += 1
        greedy_grammar_token = None
        if self.mask_invalid_tokens:
            try:
                # returns the names of the Terminals that are currently accepted.
                compilation_start_time = time.time()
                self.partial_codes.append(partial_code)
                cur_ac_terminals, next_ac_terminals, cur_term_str = self.inc_parser.get_acceptable_next_terminals(partial_code)
                self.accept_tokens_sizes.append(len(cur_ac_terminals))
                greedy_token = self.tokenizer.decode(scores.argmax(dim=-1), skip_special_tokens=True)

                #### Masking the scores ####
                if '_NL' in cur_ac_terminals or 'COMMENT' in cur_ac_terminals or 'STRING' in cur_ac_terminals or cur_term_str.startswith(' "') or cur_term_str.startswith('"') or cur_term_str.startswith(" '") or cur_term_str.startswith("'"):
                    pass
                else:
                    # Which vocab tokens can be appended to the cur_term_str and become prefix to one cur_ac_terminals
                    cur_accept_mask = self._get_cur_terminal_mask(cur_ac_terminals, cur_term_str)

                    # Which vocab tokens can be next_ac_terminals
                    next_accept_mask = self._get_next_terminal_mask(next_ac_terminals)
                    accept_mask = cur_accept_mask | next_accept_mask
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
                print("-"*80)
                print('Code lenght:', len(partial_code))
                print(partial_code)
                print(repr(partial_code))
                print('Error:', e)

        should_not_happen = greedy_grammar_token is not None and greedy_token is not None and '//' in greedy_grammar_token and '//' not in greedy_token

        if should_not_happen:
            print('Partial codes before this:')
            print(self.partial_codes)
            print(next_ac_terminals)
            raise Exception('Greedy grammar token is //')

        return scores
    