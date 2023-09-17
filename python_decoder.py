import time
import torch
from transformers import LogitsProcessor, PreTrainedTokenizer
from incremental_parser import IncrementalParser


class PythonDecoder(LogitsProcessor):
    def __init__(self, tokenizer: PreTrainedTokenizer, **kwargs):
        time_start = time.time()
        self.tokenizer = tokenizer
        self.inc_parser = IncrementalParser()
        self.debug = True
        self.token_cnt = 0

        # Iterate through the vocabulary and create a map of (tokenizer token -> grammar terminal)
        # Note: It may happen that many tokens do not fall in any category
        self.token_to_terminal = {}
        self.terminal_to_mask = {}
        self.uncategorezed_mask = torch.zeros(tokenizer.vocab_size, dtype=torch.bool)

        self.start_time = time.time()
        self.prev_time = self.start_time

        for i in range(tokenizer.vocab_size):
            token = tokenizer.decode(torch.tensor([i]), skip_special_tokens=True)
            token_type = self.inc_parser.get_matching_terminal(token)
            
            if token_type is not None:
                self.token_to_terminal[token] = token_type
            
                if not token_type in self.terminal_to_mask:
                    self.terminal_to_mask[token_type] = torch.zeros(tokenizer.vocab_size, dtype=torch.bool)
                self.terminal_to_mask[token_type][i] = True
            else:
                self.uncategorezed_mask[i] = False
        
        print(f"Found {len(self.token_to_terminal)}/{tokenizer.vocab_size} tokens that form a terminal.")
        print("Time taken for preprocessing:", time.time() - time_start)

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

        self.token_cnt += 1
        if self.debug and self.token_cnt%10==0:
            print("-"*80)
            print('Code lenght:', len(partial_code))
            print(partial_code)
            print(repr(partial_code))

            # Get the token per second
            cur_time = time.time()
            print('Current generation speed:', 10/(cur_time - self.prev_time))
            print('Total generation speed:', self.token_cnt/(cur_time - self.start_time))
            self.prev_time = cur_time

        # returns the names of the Terminals that are currently accepted.
        compilation_start_time = time.time()
        cur_ac_terminals, next_ac_terminals, cur_term_str = self.inc_parser.get_acceptable_next_terminals(partial_code)
            
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
            if self.debug and self.token_cnt%10==0:
                print("Number of acceptable tokens:", accept_mask.sum().item())
        
        greedy_grammar_token = self.tokenizer.decode(scores.argmax(dim=-1), skip_special_tokens=True)

        if greedy_token != greedy_grammar_token:
            print('Different greedy token:', repr(greedy_token), repr(greedy_grammar_token), scores.argmax(dim=-1))
            print('Greedy token:', repr(greedy_token), scores.argmax(dim=-1))
            print('Greedy grammar-based token:', repr(greedy_grammar_token), scores.argmax(dim=-1))

        if self.debug and self.token_cnt%10==0:
            print('Time taken for compilation:', time.time() - compilation_start_time)
            print("-"*80)

        return scores
    