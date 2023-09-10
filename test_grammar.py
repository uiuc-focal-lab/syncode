from lark import Lark
from lark.indenter import Indenter
from python_decoder import get_token_type
from transformers import (
    LlamaTokenizer,
    LlamaForCausalLM,
    PreTrainedModel,
    PreTrainedTokenizer,
    LogitsProcessorList
)

class PythonIndenter(Indenter):
    NL_type = "_NL"
    OPEN_PAREN_types = ["LPAR", "LSQB", "LBRACE"]
    CLOSE_PAREN_types = ["RPAR", "RSQB", "RBRACE"]
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    tab_len = 4

parser = Lark.open(
    "python_grammar.lark",
    parser="lalr",
    start="file_input",
    postlex=PythonIndenter(),
    propagate_positions=True,
)

def test_parser():
    code = f"""
    a = 3
    b = 4
    c = 5

    def f():
        ""\"
        funcdef!!!
        ""\"
        a = 4
        c = 3
        
        # Random comment
        if i == 2:
            2 + 3
            t + 1
            pass
        else:
            return
        
        return sss
    """

    print(code)
    interactive = parser.parse_interactive(code)

    print(parser.parse(code))

def test_vocab_terminals():
    tokenizer = LlamaTokenizer.from_pretrained("/share/models/llama_model/hf/7B")
    token_to_terminal = {}
    token_type_count = {}

    for i in range(tokenizer.vocab_size):
        token = tokenizer.decode(i)
        token_type = get_token_type(parser, token)
        if token_type is not None:
            token_to_terminal[token] = token_type

            # Count the number of tokens of each type
            if token_type not in token_type_count:
                token_type_count[token_type] = 0
            token_type_count[token_type] += 1
    
    print(token_type_count)
    print(f"Found {len(token_to_terminal)}/{tokenizer.vocab_size} tokens that form a terminal.")

test_vocab_terminals()