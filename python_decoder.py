import string
import time
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

def get_token_type(parser, s):
    try:
        if s == '\t':
            return '_INDENT'
        
        # Non-regex direct matches
        for t in parser.terminals:
            if t.pattern.type == 'str' and t.pattern.value == s:
                return t.name
        
        interactive = parser.parse_interactive(s)
        token = next(interactive.iter_parse())
        return token.type
    except:
        return None

def get_acceptable_next_tokens(parser, code):
    interactive = parser.parse_interactive(code)
    
    for token in interactive.lexer_thread.lex(interactive.parser_state):
            # print(repr(token))
            if token.type == '_DEDENT':
                continue
            _ = interactive.feed_token(token)
    
    print('Acceptable Tokens:', interactive.accepts())
    return interactive.accepts()


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
            token_type = get_token_type(self.parser, token)
            
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
        acceptable_token_types = get_acceptable_next_tokens(self.parser, partial_code)

        accept_mask = self.uncategorezed_mask.clone()
        # print(accept_mask.sum())

        for token_type in acceptable_token_types:
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
    