import string
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
        interactive = parser.parse_interactive(s)
        token = next(interactive.iter_parse())
        return token.type
    except:
        return None

class PythonDecoder(LogitsProcessor):
    
    def __init__(self, tokenizer: PreTrainedTokenizer, **kwargs):
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
        for i in range(tokenizer.vocab_size):
            token = tokenizer.decode(i)
            token_type = get_token_type(self.parser, token)
            if token_type is not None:
                self.token_to_terminal[token] = token_type
        
        print(f"Found {len(self.token_to_terminal)}/{tokenizer.vocab_size} tokens that form a terminal.")


    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:
        partial_code = self.tokenizer.decode(input_ids[0], skip_special_tokens=True)
        interactive = self.parser.parse_interactive(partial_code)
        # feeds the text given to above into the parsers. This is not done automatically.
        interactive.exhaust_lexer()

        # returns the names of the Terminals that are currently accepted.
        print(interactive.accepts())
        return scores
    