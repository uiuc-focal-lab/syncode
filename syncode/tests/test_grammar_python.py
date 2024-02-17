import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from parsers.python_parser import PythonIncrementalParser
from parsers import create_parser
from common import run_tests
from transformersm import (
    LlamaTokenizer,
)
from parse_result import AcceptSequence, RemainderState
from parsers.grammars.grammar import Grammar

python_grammar = Grammar('python')
inc_parser = create_parser(python_grammar)

def test_vocab_terminals():
    tokenizer = LlamaTokenizer.from_pretrained("/share/models/llama_model/hf/7B")

    token_to_terminal = {}
    token_type_count = {}
    inc_parser.reset()

    for i in range(tokenizer.vocab_size):
        token = tokenizer.decode(i)
        token_type = inc_parser.get_matching_terminal(token)
        if token_type is not None:
            token_to_terminal[token] = token_type

            # Count the number of tokens of each type
            if token_type not in token_type_count:
                token_type_count[token_type] = 0

            token_type_count[token_type] += 1

    print(token_type_count)
    print(f"Found {len(token_to_terminal)}/{tokenizer.vocab_size} tokens that form a terminal.")

def test_parser0():
    
    code = f"""
def foo():
    x = 9
    if bar:
        baz()
        x = 1
        y = 2
        z = 1 +
"""
    r  = inc_parser.get_acceptable_next_terminals(code)
    print(r.next_accept_terminals)

def test_parser1():
    inc_parser.reset()
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
    inc_parser.get_acceptable_next_terminals(code)

def test_parser2():
    inc_parser.reset()
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t\n\ta=3+5\n\tb='
    r = inc_parser.get_acceptable_next_terminals(partial_code)
    assert AcceptSequence(['EQUAL', 'FLOAT_NUMBER']) in r.accept_sequences

def test_parser3(): 
    inc_parser.reset()
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t\n\tfor i in range(len(numbers) -1, -1, -1) :\n\t\tfor j in range(i+1, len(numbers) ,1) :\n\t\t\tif abs(numbers[i] - numbers[j] ) < threshold :\n\t\t\t\treturn True\n'
    r = inc_parser.get_acceptable_next_terminals(partial_code)
    assert r.next_ac_indents.accept_indents == [0, 4, 8, 12, 16]

def test_parser4():
    inc_parser.reset()
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t\n\tfor i in range(len(numbers) -1, -1, -1) :\n\t\tfor j in range(i+1, len(numbers) ,1) :\n\t\t\tif abs(numbers[i] - numbers[j] ) < threshold :\n'
    r = inc_parser.get_acceptable_next_terminals(partial_code)
    assert r.next_ac_indents.greater_than_indent_val == 12

def test_parser5():
    inc_parser.reset()
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t\n\tfor i in range(len(numbers) -1, -1, -1) :\n\t\tfor j in range(i+1, len(numbers) ,1) :\n\t\t\tif abs(numbers[i] - numbers[j] ) < threshold :\n\t\t\t\treturn True\n\t\t\t\t'
    # There cannot be another tab after this
    r = inc_parser.get_acceptable_next_terminals(partial_code)
    r.next_ac_indents.accept_indents == [0]

def test_parser6():
    inc_parser.reset()
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t\n\tfor i in range(len(numbers) -1, -1, -1) :\n\t\tfor j in range(i+1, len(numbers) ,1) :\n\t\t\tif abs(numbers[i] - numbers[j] ) < threshold :\n\t\t\t\treturn True\n\n\n\t\t\t\t'
    # There cannot be another tab after this
    r = inc_parser.get_acceptable_next_terminals(partial_code)
    assert r.next_ac_indents.accept_indents == [0]

    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t\n\tfor i in range(len(numbers) -1, -1, -1) :\n\t\tfor j in range(i+1, len(numbers) ,1) :\n\t\t\tif abs(numbers[i] - numbers[j] ) < threshold :\n\t\t\t\treturn True\n\n\t\t\t\n\t\t'
    # There can be another tab after this
    r = inc_parser.get_acceptable_next_terminals(partial_code)
    assert r.next_ac_indents.accept_indents == [0, 4, 8]

def test_parser7():
    inc_parser.reset()
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\tfor i in range(len(numbers) -1, -1, -1) :\n\t\tif numbers[i] - numbers[i+1] < threshold:\n\t\t\treturn True\n\treturn False\n'
    r = inc_parser.get_acceptable_next_terminals(partial_code)
    # assert '_TAB' in r.next_accept_terminals
    assert AcceptSequence(['_NL', '_NL']) in r.accept_sequences
    assert r.next_ac_indents.accept_indents == [0, 4]

def test_parser8():
    inc_parser.reset()
    partial_code = 'def separate_paren_groups(paren_string: str) -> List[str]:\n\tfor i in paren_string:\n\t\tif i == \''
    # Check if the whitespaces are being ignored
    r = inc_parser.get_acceptable_next_terminals(partial_code)
    assert r.remainder == "'" # This should not be " '"

def test_parser9():
    inc_parser.reset()
    partial_code = 'from typing import List\n\n\ndef separate_paren_groups(paren_string: str) -> List[str]:\n\tpar = []\n\tfor i in par:\n\t\tif i == \'Hello'
    r = inc_parser.get_acceptable_next_terminals(partial_code)
    print(r.remainder)
    assert r.remainder == "'Hello"

def test_parser10():
    inc_parser.reset()
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t""" Check if in given list of numbers, are any two numbers closer to each other than\n\tgiven threshold.\n\t>>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n\tFalse\n\t>>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n\tTrue\n\t"""\n\tfor i in range(len(numbers) -1, -1, -1):\n\t\tfor j in range(i+1, len(numbers) -1, -1):\n\t\t\tif abs(numbers[i] - numbers[j] ) < threshold:\n\t\t\t\treturn True\n\treturn False\n\n\ndef has_close_elements_with_threshold(numbers: List[float] , threshold: float) -> bool:\n\t""'
    r = inc_parser.get_acceptable_next_terminals(partial_code)
    print(repr(r.remainder))
    assert r.remainder == '""'

def test_parser11():
    inc_parser.reset()
    partial_codes = ['from typing import List, Tuple\n\n\ndef rolling_max(numbers: List[int]) -> List[int]:\n\t""" From a given list of integers, generate a list of rolling maximum element found until given moment\n\tin the sequence.\n\t>>> rolling_max([1, 2, 3, 2, 3, 4, 2])\n\t[1, 2, 3, 3, 3, 4, 4]\n\t"""\n\tresult = []\n\tfor i in range(len(numbers)):\n\t\tif i == len(numbers) - 1:  # if we are at the end of the sequence\n\t\t\tresult.append(numbers[i]) ']
    r = inc_parser.get_acceptable_next_terminals(partial_codes[-1])
    assert AcceptSequence(['COMMENT']) in r.accept_sequences

def test_parser12(): 
    inc_parser.reset()
    partial_code = 'from typing import List\n\n\ndef rescale_to_unit(numbers: List[float]) -> List[float]:\n\t""" Given list of numbers (of at least two elements), apply a linear transform to that list,\n\tsuch that the smallest number will become 0 and the largest will become 1\n\t>>> rescale_to_unit([1.0, 2.0, 3.0, 4.0, 5.0])\n\t[0.0, 0.25, 0.5, 0.75, 1.0]\n\t"""\n\tfor i in x: # this is'
    # This should not crash. Earlier version was crashing on this
    r = inc_parser.get_acceptable_next_terminals(partial_code)

def test_parser13():
    inc_parser.reset()
    partial_code =  'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t""" Check if in given list of numbers, are any two numbers closer to each other than\n\tgiven threshold.\n\t>>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n\tFalse\n\t>>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n\tTrue\n\t"""\n\tfor i in range(len(numbers)):\n\t\tfor j in range(i + 1, len(numbers)):\n\t\t\tif abs(numbers[i] - numbers[j]) < threshold:\n\t\t\t\treturn True\n\treturn False\n\n\ndef has_close_elements_in_range(numbers: List[float], lower_bound: float, upper_bound: float) -> bool:\n\t"""'
    # First two " from """ should not match with the STRING
    r = inc_parser.get_acceptable_next_terminals(partial_code)
    assert r.remainder == '"""'

def test_parser14():
    inc_parser.reset()
    partial_code = 'def has_close_elements_in_range(numbers: List[float], range_start: float, range_end: float) -> bool:\n\t""" Check if in given list of numbers, are any two numbers closer to each other than given range. """'
    r = inc_parser.get_acceptable_next_terminals(partial_code)
    assert r.remainder.startswith('\n\t"""') # _NL consumes \n, \t and comments

def test_parser15():
    inc_parser.reset()
    partial_code = 'from typing import List, Tuple\n\n\ndef find_closest_elements(numbers: List[float]) -> Tuple[float, float]:\n\t""" From a supplied list of numbers (of length at least two) select and return two that are the closest to each\n\tother and return them in order (smaller number, larger number).\n\t>>> find_closest_elements([1.0, 2.0, 3.0, 4.0, 5.0, 2.2])\n\t(2.0, 2.2)\n\t>>> find_closest_elements([1.0, 2.0, 3.0, 4.0, 5.0, 2.0])\n\t(2.0, 2.0)\n\t"""\n\tif len(numbers) < 2:\n\t\treturn None\n\tclos'
    r = inc_parser.get_acceptable_next_terminals(partial_code)
    assert r.remainder == 'clos' # Should not consider _DEDENT as final terminal

def test_parser16():
    # Case 1:
    partial_code = '\n\ndef neg_nos(list1):\n  for num in list1:\n    if num < 0:\n      print '
    inc_parser.get_acceptable_next_terminals(partial_code)
    r = inc_parser.get_acceptable_next_terminals(partial_code)
    assert r.remainder_state == RemainderState.COMPLETE

    # Case 2:
    partial_code = '\n\ndef neg_nos(list1):\n  for num in list1:\n    if num < 0:\n      print'
    r = inc_parser.get_acceptable_next_terminals(partial_code)
    assert r.remainder_state == RemainderState.MAYBE_COMPLETE

def test_parser17():
    # Checking if the parser is able to handle the case where one of the function only has a docstring
    inc_parser.reset()
    code = f"""
def cat():
    ''' something '''
def"""
    r  = inc_parser.get_acceptable_next_terminals(code)
    assert AcceptSequence(['DEF', 'NAME']) in r.accept_sequences

def test_parser18():
    # Tests if indentation check works non-incrementally
    code = f"""
def cat():
    ''' something '''
    x = 3

"""
    inc_parser.reset()
    r  = inc_parser.get_acceptable_next_terminals(code)
    print(r.next_ac_indents)
    assert r.next_ac_indents.accept_indents == [0, 4]

    code = f"""
def cat():
    ''' something '''
    if True:
      x = 3
    else:
    
""" 
    inc_parser.reset()
    r  = inc_parser.get_acceptable_next_terminals(code)
    print(r.next_ac_indents)
    assert r.next_ac_indents.greater_than_indent_val == 4 
    
    code = f"""
def cat():
    ''' something '''
    if True:
      if True:
        x = 3

"""
    inc_parser.reset()
    r  = inc_parser.get_acceptable_next_terminals(code)
    print(r.next_ac_indents)
    assert r.next_ac_indents.accept_indents == [0, 4, 6, 8]

def test_parser19():
    # LONG_STRING indentation is checked
    partial_code =  '\n\ndef smallest_num(xs):\n  """\n  Write a python function to find smallest number in a list.\n  >>> smallest_num([10, 20, 1, 45, 99])\n  1\n  >>> smallest_num([1, 2, 3])\n  1\n  >>> smallest_num([45, 46, 50, 60])\n  45\n  """\n '
    inc_parser.reset()
    r = inc_parser.get_acceptable_next_terminals(partial_code)
    assert r.next_ac_indents.accept_indents == [1]

    partial_code = '\n\ndef find_rect_num(n):\n  """\n  Write a function to find the n-th rectangular number.\n  >>> find_rect_num(4)\n  20\n  >>> find_rect_num(5)\n  30\n  >>> find_rect_num(6)\n  42\n  """\n  n = int(n)\n  if n < 0:\n   '
    inc_parser.reset()
    r = inc_parser.get_acceptable_next_terminals(partial_code)
    assert r.next_ac_indents.greater_than_indent_val == -1


def test_incremental_parser():
    inc_parser.reset()
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t""" Check if in given list of numbers, are any two numbers closer to each other than\n\tgiven threshold.\n\t>>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n\tFalse\n\t>>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n\tTrue\n\t"""\n\tfor i in range(len(numbers) -1, -1, -1):\n\t\tfor j in range(i+1, len(numbers) -1, -1):\n\t\t\tif abs(numbers[i] - numbers[j] ) < threshold:\n\t\t\t\treturn True\n\treturn False\n\n\ndef has_close_elements_with_threshold(numbers: List[float] , threshold: float) -> bool:\n\t""'
    r = inc_parser.get_acceptable_next_terminals(partial_code[:len(partial_code)-10])
    r = inc_parser.get_acceptable_next_terminals(partial_code)
    assert r.remainder == '""'

def test_incremental_parser2():
    inc_parser.reset()
    prompt = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t""" Check if in given list of numbers, are any two numbers closer to each other than\n\tgiven threshold.\n\t>>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n\tFalse\n\t>>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n\tTrue\n'

    generated_code = '\t"""\n\tfor i in range(len(numbers) -1, -1, -1):\n\t\tfor j in range(i+1, len(numbers) -1, -1):\n\t\t\tif abs(numbers[i] - numbers[j] ) < threshold:\n\t\t\t\treturn True\n\treturn False\n\n\ndef has_close_elements_with_threshold(numbers: List[float] , threshold: float) -> bool:\n\ta="shu'

    i = 0
    while i<len(generated_code):
        i += 2
        r = inc_parser.get_acceptable_next_terminals(prompt + generated_code[:i])
    assert r.remainder == '"shu'
    assert r.next_ac_indents == None

def test_incremental_parser3():
    inc_parser.reset()
    new_inc_parser = create_parser(python_grammar)
    partial_codes = ['from typing import List\n\n\ndef rescale_to_unit(numbers: List[float]) -> List[float]:\n\t""" Given list of numbers (of at least two elements), apply a linear transform to that list,\n\tsuch that the smallest number will become 0 and the largest will become 1\n\t>>> rescale_to_unit([1.0, 2.0, 3.0, 4.0, 5.0])\n\t[0.0, 0.25, 0.5, 0.75, 1.0]\n\t"""\n\tmin_num = min(numbers)\n\tmax_num = max(numbers)\n\treturn [min_num * (x - min_num) / (max_num - min_num) + min_num for x in numbers]\n\n', 'from typing import List\n\n\ndef rescale_to_unit(numbers: List[float]) -> List[float]:\n\t""" Given list of numbers (of at least two elements), apply a linear transform to that list,\n\tsuch that the smallest number will become 0 and the largest will become 1\n\t>>> rescale_to_unit([1.0, 2.0, 3.0, 4.0, 5.0])\n\t[0.0, 0.25, 0.5, 0.75, 1.0]\n\t"""\n\tmin_num = min(numbers)\n\tmax_num = max(numbers)\n\treturn [min_num * (x - min_num) / (max_num - min_num) + min_num for x in numbers]\n\n\n', 'from typing import List\n\n\ndef rescale_to_unit(numbers: List[float]) -> List[float]:\n\t""" Given list of numbers (of at least two elements), apply a linear transform to that list,\n\tsuch that the smallest number will become 0 and the largest will become 1\n\t>>> rescale_to_unit([1.0, 2.0, 3.0, 4.0, 5.0])\n\t[0.0, 0.25, 0.5, 0.75, 1.0]\n\t"""\n\tmin_num = min(numbers)\n\tmax_num = max(numbers)\n\treturn [min_num * (x - min_num) / (max_num - min_num) + min_num for x in numbers]\n\n\ndef']
    for i, partial_code in enumerate(partial_codes):
        new_inc_parser.reset()
        r1 = inc_parser.get_acceptable_next_terminals(partial_code)
        r2 = new_inc_parser.get_acceptable_next_terminals(partial_code)
        
        assert r1.accept_sequences == r2.accept_sequences, f"Failed at {i} where \nr1 = {r1.accept_sequences} \nr2 = {r2.accept_sequences}"

def test_incremental_parser4():
    inc_parser.reset()
    new_inc_parser = create_parser(python_grammar)
    partial_codes = ['\n\ndef derivative(xs: list):\n\t""" xs represent coefficients of a polynomial.\n\txs[0] + xs[1] * x + xs[2] * x^2 + ....\n\t Return derivative of this polynomial in the same form.\n\t>>> derivative([3, 1, 2, 4, 5])\n\t[1, 4, 12, 20]\n\t>>> derivative([1, 2, 3])\n\t[2, 6]\n\t"""\n\txs = list(xs)', '\n\ndef derivative(xs: list):\n\t""" xs represent coefficients of a polynomial.\n\txs[0] + xs[1] * x + xs[2] * x^2 + ....\n\t Return derivative of this polynomial in the same form.\n\t>>> derivative([3, 1, 2, 4, 5])\n\t[1, 4, 12, 20]\n\t>>> derivative([1, 2, 3])\n\t[2, 6]\n\t"""\n\txs = list(xs)\n', '\n\ndef derivative(xs: list):\n\t""" xs represent coefficients of a polynomial.\n\txs[0] + xs[1] * x + xs[2] * x^2 + ....\n\t Return derivative of this polynomial in the same form.\n\t>>> derivative([3, 1, 2, 4, 5])\n\t[1, 4, 12, 20]\n\t>>> derivative([1, 2, 3])\n\t[2, 6]\n\t"""\n\txs = list(xs)\n\t']
    for i, partial_code in enumerate(partial_codes):
        new_inc_parser.reset()
        r1 = inc_parser.get_acceptable_next_terminals(partial_code)
        r2 = new_inc_parser.get_acceptable_next_terminals(partial_code)
        assert r1.accept_sequences == r2.accept_sequences, i

def test_parser20():
    inc_parser.reset()
    partial_code = "def separate_paren_groups(paren_string: str) -> List[str]:\n\treturn [paren_string.strip() for paren_string in paren_string.split('"
    r = inc_parser.get_acceptable_next_terminals(partial_code)
    print(r)
    assert r.remainder == "'"
    assert AcceptSequence(['STRING']) in r.accept_sequences

def test_parser21():
    inc_parser.reset()
    partial_code = "def factorize(n: int) -> List[int]:\n\tfactors = []\n\tfor i in range(2, n + 1):\n\t\t"
    r = inc_parser.get_acceptable_next_terminals(partial_code)
    assert AcceptSequence(['_NL', '_NL']) in r.accept_sequences
    assert r.remainder == '\n\t\t'

def test_parser22():
    inc_parser.reset()
    partial_code = "def intersperse(numbers: List[int], delimeter: int) -> List[int]:\n\treturn [n for n in numbers if n % 2 == 0 and n // 2 == del"

    r = inc_parser.get_acceptable_next_terminals(partial_code)
    assert r.remainder == 'del'
    assert AcceptSequence(['NAME']) in r.accept_sequences

def test_parser23():
    inc_parser.reset()
    partial_code = "def make_palindrome(string: str) -> str:\n\t#"
    r = inc_parser.get_acceptable_next_terminals(partial_code)
    assert AcceptSequence(['COMMENT']) in r.accept_sequences

tests = [test_parser1, test_parser2, test_parser3, test_parser4, test_parser5, test_parser6, test_parser7, test_parser8, test_parser9, test_parser10, test_parser11, test_parser12, test_parser13, test_parser14, test_parser15, test_parser16, test_parser17, test_parser18, test_parser19, test_parser20, test_parser21, test_parser22, test_parser23, test_incremental_parser, test_incremental_parser2, test_incremental_parser3, test_incremental_parser4]
# tests = [test_parser11]
run_tests(tests)
