import string
import time
import re
import torch
from transformers import LogitsProcessor, PreTrainedTokenizer
from lark import Lark
from lark.indenter import Indenter

class PythonIndenter(Indenter):
    NL_type = "_NL"
    OPEN_PAREN_types = ["LPAR", "LSQB", "LBRACE"]
    CLOSE_PAREN_types = ["RPAR", "RSQB", "RBRACE"]
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    tab_len = 4

def get_matching_terminal(parser, s):
    # Special cases
    if s == '\t':
        return '_TAB'
    
    # Non-regex direct matches
    for t in parser.terminals:
        if t.pattern.type == 'str' and t.pattern.value == s:
            return t.name
    
    # Regex matches
    for t in parser.terminals:
        if t.pattern.type == 're' and re.match(t.pattern.value, s):
            return t.name

    # TODO: Use priorities to resolve conflicts
    return None

def get_acceptable_next_terminals(parser, code):
    interactive = parser.parse_interactive(code)
    token_seq = []
    dedent_q = []
    cur_indentation_level = 0
    cur_ac_terminals = None
    next_ac_terminals = None

    for token in interactive.lexer_thread.lex(interactive.parser_state):
            if token.type == '_INDENT':
                cur_indentation_level += 1
            
            if token.type == '_DEDENT':
                # Do not shoot dedent tokens unless there is some code on the next line
                dedent_q.append(token)
                continue
            else:
                # Shoot all the dedent tokens that are in the queue
                while not len(dedent_q)==0:
                    dedent_token = dedent_q.pop()
                    cur_indentation_level -= 1
                    interactive.feed_token(dedent_token)
                    token_seq.append(dedent_token)

            # TODO: Check if there is an overhead of computing accept tokens
            cur_ac_terminals = next_ac_terminals
            next_ac_terminals = interactive.accepts()

            interactive.feed_token(token)
            token_seq.append(token)
    
    next_ac_terminals = interactive.accepts()

    if token_seq[-1].type == '_NL':
        # Compute next line accepted indentation levels
        max_next_indentation_level = 0
        if '_INDENT' in next_ac_terminals:
            max_next_indentation_level = cur_indentation_level + 1
        elif '_DEDENT' in next_ac_terminals and len(next_ac_terminals)==1:
            max_next_indentation_level = cur_indentation_level - 1
        elif '_DEDENT' in next_ac_terminals and len(next_ac_terminals)>1:
            max_next_indentation_level = cur_indentation_level

        cur_tabs = token_seq[-1].value.split('\n')[-1].count('\t')
        # print('cur_tabs:', cur_tabs, 'max_next_indentation_level:', max_next_indentation_level)

        # Remove the _INDENT and _DEDENT tokens from the acceptable tokens
        # since we inform the indentation level through the _TAB token
        if '_INDENT' in next_ac_terminals:
            next_ac_terminals.remove('_INDENT')
        if '_DEDENT' in next_ac_terminals:
            next_ac_terminals.remove('_DEDENT')

        # '_NL' is always accepted in this case
        next_ac_terminals.add('_NL')

        if cur_tabs < max_next_indentation_level:
            print('Expect a tab!')
            next_ac_terminals.add('_TAB')
        elif cur_tabs > max_next_indentation_level:
            raise Exception('Invalid indentation level! max_next_indentation_level: {}, cur_tabs: {}'.format(max_next_indentation_level, cur_tabs))

    # print('Token sequence:', token_seq)
    print('Acceptable Tokens:', next_ac_terminals)
    return cur_ac_terminals, next_ac_terminals


class PythonDecoder(LogitsProcessor):
    
    def __init__(self, tokenizer: PreTrainedTokenizer, **kwargs):
        time_start = time.time()
        self.tokenizer = tokenizer
        self.parser = Lark.open(
            "python_grammar.lark",
            parser="lalr",
            start="file_input",
            postlex=PythonIndenter(),
            propagate_positions=True,
        )

        # Iterate through the vocabulary and create a map of (tokenizer token -> grammar terminal)
        # Note: It may happen that many tokens do not fall in any category
        self.token_to_terminal = {}
        self.terminal_to_mask = {}
        self.uncategorezed_mask = torch.zeros(tokenizer.vocab_size, dtype=torch.bool)

        for i in range(tokenizer.vocab_size):
            token = tokenizer.decode(torch.tensor([i]), skip_special_tokens=True)
            token_type = get_matching_terminal(self.parser, token)
            
            if token_type is not None:
                self.token_to_terminal[token] = token_type
            
                if not token_type in self.terminal_to_mask:
                    self.terminal_to_mask[token_type] = torch.zeros(tokenizer.vocab_size, dtype=torch.bool)
                self.terminal_to_mask[token_type][i] = True
            else:
                self.uncategorezed_mask[i] = False
        
        print(f"Found {len(self.token_to_terminal)}/{tokenizer.vocab_size} tokens that form a terminal.")
        print("Time taken for preprocessing:", time.time() - time_start)


    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:
        partial_code = self.tokenizer.decode(input_ids[0], skip_special_tokens=True)

        print("-"*80)
        print('Code lenght:', len(partial_code))

        print(partial_code)
        print(repr(partial_code))

        # returns the names of the Terminals that are currently accepted.
        cur_ac_terminals, next_ac_terminals = get_acceptable_next_terminals(self.parser, partial_code)

        accept_mask = self.uncategorezed_mask.clone()
        # print(accept_mask.sum())

        for token_type in next_ac_terminals:
            if token_type in self.terminal_to_mask:
                accept_mask |= self.terminal_to_mask[token_type]
            # print(accept_mask.sum())
        
        print("Number of acceptable tokens:", accept_mask.sum().item())
        print("-"*80)

        greedy_token = self.tokenizer.decode(scores.argmax(dim=-1), skip_special_tokens=True)
        print('Greedy token:', repr(greedy_token), scores.argmax(dim=-1))

        scores = scores.masked_fill(~accept_mask.to(scores.device), -float("inf"))
    
        greedy_grammar_token = self.tokenizer.decode(scores.argmax(dim=-1), skip_special_tokens=True)
        print('Greedy grammar-based token:', repr(greedy_grammar_token), scores.argmax(dim=-1))
        return scores
    