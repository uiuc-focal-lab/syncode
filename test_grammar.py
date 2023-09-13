import sys
import traceback
import torch
from lark import Lark
from lark.indenter import Indenter
from python_decoder import get_acceptable_next_terminals, get_matching_terminal
from transformers import (
    LlamaTokenizer,
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
        token_type = get_matching_terminal(parser, token)
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
    get_acceptable_next_terminals(parser, code)


def test_parser2():
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t""" Check if in given list of numbers, are any two numbers closer to each other than\n\tgiven threshold.\n\t>>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n\tFalse\n\t>>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n\tTrue\n\t"""\n\ta=3+5\n\tb='
    _, next_ac_terminals, _ = get_acceptable_next_terminals(parser, partial_code)
    assert 'FLOAT_NUMBER' in next_ac_terminals

def test_parser3():
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t""" Check if in given list of numbers, are any two numbers closer to each other than\n\tgiven threshold.\n\t>>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n\tFalse\n\t>>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n\tTrue\n\t"""\n\tfor i in range(len(numbers) -1, -1, -1) :\n\t\tfor j in range(i+1, len(numbers) ,1) :\n\t\t\tif abs(numbers[i] - numbers[j] ) < threshold :\n\t\t\t\treturn True\n'
    _, next_ac_terminals, _ = get_acceptable_next_terminals(parser, partial_code)
    assert '_TAB' in next_ac_terminals

def test_parser4():
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t""" Check if in given list of numbers, are any two numbers closer to each other than\n\tgiven threshold.\n\t>>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n\tFalse\n\t>>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n\tTrue\n\t"""\n\tfor i in range(len(numbers) -1, -1, -1) :\n\t\tfor j in range(i+1, len(numbers) ,1) :\n\t\t\tif abs(numbers[i] - numbers[j] ) < threshold :\n'
    _, next_ac_terminals, _ = get_acceptable_next_terminals(parser, partial_code)
    assert '_TAB' in next_ac_terminals

def test_parser5():
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t\n\tfor i in range(len(numbers) -1, -1, -1) :\n\t\tfor j in range(i+1, len(numbers) ,1) :\n\t\t\tif abs(numbers[i] - numbers[j] ) < threshold :\n\t\t\t\treturn True\n\t\t\t\t'
    # There cannot be another tab after this
    _, next_ac_terminals, _ = get_acceptable_next_terminals(parser, partial_code)
    assert '_TAB' not in next_ac_terminals

def test_parser6():
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t\n\tfor i in range(len(numbers) -1, -1, -1) :\n\t\tfor j in range(i+1, len(numbers) ,1) :\n\t\t\tif abs(numbers[i] - numbers[j] ) < threshold :\n\t\t\t\treturn True\n\n\n\t\t\t\t'
    # There cannot be another tab after this
    _, next_ac_terminals, _ = get_acceptable_next_terminals(parser, partial_code)
    assert '_TAB' not in next_ac_terminals

def test_parser6():
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t\n\tfor i in range(len(numbers) -1, -1, -1) :\n\t\tfor j in range(i+1, len(numbers) ,1) :\n\t\t\tif abs(numbers[i] - numbers[j] ) < threshold :\n\t\t\t\treturn True\n\n\t\t\t\n\t\t'
    # There can be another tab after this
    _, next_ac_terminals, _ = get_acceptable_next_terminals(parser, partial_code)
    assert '_TAB' in next_ac_terminals

def test_parser7():
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t""" Check if in given list of numbers, are any two numbers closer to each other than\n\tgiven threshold.\n\t>>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n\tFalse\n\t>>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n\tTrue\n\t"""\n\tfor i in range(len(numbers) -1, -1, -1) :\n\t\tif numbers[i] - numbers[i+1] < threshold:\n\t\t\treturn True\n\treturn False\n'
    _, next_ac_terminals, _ = get_acceptable_next_terminals(parser, partial_code)
    assert '_TAB' in next_ac_terminals
    assert '_NL' in next_ac_terminals

def test_parser8():
    partial_code = 'from typing import List\n\n\ndef separate_paren_groups(paren_string: str) -> List[str]:\n\tpar = []\n\tfor i in par:\n\t\tif i == \''
    _, next_ac_terminals, cur_term_str = get_acceptable_next_terminals(parser, partial_code)
    assert cur_term_str == "'"

def test_parser9():
    partial_code = 'from typing import List\n\n\ndef separate_paren_groups(paren_string: str) -> List[str]:\n\tpar = []\n\tfor i in par:\n\t\tif i == \'Hello'
    _, next_ac_terminals, cur_term_str = get_acceptable_next_terminals(parser, partial_code)
    print(cur_term_str)
    assert cur_term_str == "'Hello"

def test_get_matching_terminals():
    assert get_matching_terminal(parser, "\t") == "_TAB"
    assert get_matching_terminal(parser, tokenizer.decode(torch.tensor([12]), skip_special_tokens=True)) == "_TAB"
    
    assert get_matching_terminal(parser, "\n") == "_NL"
    assert get_matching_terminal(parser, tokenizer.decode(torch.tensor([13]), skip_special_tokens=True)) == "_NL"
    
    # Keywords
    assert get_matching_terminal(parser, "def") == "DEF"
    assert get_matching_terminal(parser, "in") == "IN"
    assert get_matching_terminal(parser, "if") == "IF"
    assert get_matching_terminal(parser, "else") == "ELSE"
    assert get_matching_terminal(parser, "elif") == "ELIF"
    assert get_matching_terminal(parser, "for") == "FOR"
    assert get_matching_terminal(parser, "while") == "WHILE"
    assert get_matching_terminal(parser, "try") == "TRY"
    assert get_matching_terminal(parser, "except") == "EXCEPT"
    assert get_matching_terminal(parser, "finally") == "FINALLY"
    assert get_matching_terminal(parser, "with") == "WITH"
    assert get_matching_terminal(parser, "class") == "CLASS"

    # Regex
    assert get_matching_terminal(parser, "1234") == "DEC_NUMBER"
    assert get_matching_terminal(parser, "12.34") == "FLOAT_NUMBER"
    assert get_matching_terminal(parser, "pqr") == "NAME"
    assert get_matching_terminal(parser, "\'ssss\'") == "STRING"
    assert get_matching_terminal(parser, '\"ssss\"') == "STRING"
    assert get_matching_terminal(parser, '\"""ssss\"""') == "COMMENT"
    assert get_matching_terminal(parser, '\"""ssss') == None


tests = [test_get_matching_terminals, test_vocab_terminals, test_parser1, test_parser2, test_parser3, test_parser4, test_parser5, test_parser6, test_parser7, test_parser8, test_parser9]
tests = [test_parser8]

test_result = {}

for test in tests:
    print(f"Running test {test.__name__}")
    try:
        test()
        print(f"Test {test.__name__} passed.")
        test_result[test.__name__] = 'passed'
    except AssertionError:
        _, _, tb = sys.exc_info()
        traceback.print_tb(tb) # Fixed format
        tb_info = traceback.extract_tb(tb)
        filename, line, func, text = tb_info[-1]
        print('An error occurred on line {} in statement {}'.format(line, text))
        test_result[test.__name__] = 'failed'
    except Exception as e:
        print(f"Test {test.__name__} failed.")
        print(e)
        test_result[test.__name__] = 'failed'
    
    print("-"*80)

tests_passed = 0
for test_name, result in test_result.items():
    if result == 'passed':
        tests_passed += 1
        # Use green color for passed tests
        print(f"\033[92m{test_name}: {result}\033[0m")
    else:
        # Use red color for failed tests
        print(f"\033[91m{test_name}: {result}\033[0m")
print(f"Passed {tests_passed}/{len(tests)} tests.")
