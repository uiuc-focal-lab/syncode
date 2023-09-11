import torch
from lark import Lark
from lark.indenter import Indenter
from python_decoder import get_acceptable_next_tokens, get_token_type
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

tokenizer = LlamaTokenizer.from_pretrained("/share/models/llama_model/hf/7B")

def test_vocab_terminals():
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


def test_parser1():
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
    get_acceptable_next_tokens(parser, code)


def test_parser2():
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t""" Check if in given list of numbers, are any two numbers closer to each other than\n\tgiven threshold.\n\t>>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n\tFalse\n\t>>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n\tTrue\n\t"""\n\ta=3+5\n\tb='
    get_acceptable_next_tokens(parser, partial_code)

def test_parser3():
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t""" Check if in given list of numbers, are any two numbers closer to each other than\n\tgiven threshold.\n\t>>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n\tFalse\n\t>>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n\tTrue\n\t"""\n\tfor i in range(len(numbers) -1, -1, -1) :\n\t\tfor j in range(i+1, len(numbers) ,1) :\n\t\t\tif abs(numbers[i] - numbers[j] ) < threshold :\n\t\t\t\treturn True\n'
    acc_tokens = get_acceptable_next_tokens(parser, partial_code)
    print(acc_tokens)
    # assert '_INDENT' in acc_tokens

def test_parser4():
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t""" Check if in given list of numbers, are any two numbers closer to each other than\n\tgiven threshold.\n\t>>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n\tFalse\n\t>>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n\tTrue\n\t"""\n\tfor i in range(len(numbers) -1, -1, -1) :\n\t\tfor j in range(i+1, len(numbers) ,1) :\n\t\t\tif abs(numbers[i] - numbers[j] ) < threshold :\n'
    acc_tokens = get_acceptable_next_tokens(parser, partial_code)
    assert '_INDENT' in acc_tokens

def test_get_token_type():
    assert get_token_type(parser, "\t") == "_INDENT"
    assert get_token_type(parser, tokenizer.decode(torch.tensor([12]), skip_special_tokens=True)) == "_INDENT"
    
    assert get_token_type(parser, "\n") == "_NL"
    assert get_token_type(parser, tokenizer.decode(torch.tensor([13]), skip_special_tokens=True)) == "_NL"
    
    assert get_token_type(parser, "def") == "DEF"
    assert get_token_type(parser, "in") == "IN"
    assert get_token_type(parser, "if") == "IF"
    assert get_token_type(parser, "else") == "ELSE"
    assert get_token_type(parser, "elif") == "ELIF"
    assert get_token_type(parser, "for") == "FOR"
    assert get_token_type(parser, "while") == "WHILE"
    assert get_token_type(parser, "try") == "TRY"
    assert get_token_type(parser, "except") == "EXCEPT"
    assert get_token_type(parser, "finally") == "FINALLY"
    assert get_token_type(parser, "with") == "WITH"
    assert get_token_type(parser, "class") == "CLASS"

tests = [test_get_token_type, test_vocab_terminals, test_parser1, test_parser2, test_parser3, test_parser4]

for test in tests:
    print(f"Running test {test.__name__}")
    try:
        test()
        print(f"Test {test.__name__} passed.")
    except Exception as e:
        print(f"Test {test.__name__} failed.")
        print(e)
    print("-"*80)