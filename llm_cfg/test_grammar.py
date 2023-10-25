from incremental_parser import IncrementalParser
from common import run_tests
from transformers import (
    LlamaTokenizer,
)

def test_vocab_terminals():
    tokenizer = LlamaTokenizer.from_pretrained("/share/models/llama_model/hf/7B")

    token_to_terminal = {}
    token_type_count = {}
    inc_parser = IncrementalParser()

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
    inc_parser = IncrementalParser()
    code = f"""
def foo():
    x = 9
    if bar:
        baz()
        x = 1
        y = 2
        z = 1 +
"""
    _, next_ac_terminals, _  = inc_parser.get_acceptable_next_terminals(code)
    print(next_ac_terminals)

def test_parser1():
    inc_parser = IncrementalParser()
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
    inc_parser = IncrementalParser()
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t\n\ta=3+5\n\tb='
    _, next_ac_terminals, _ = inc_parser.get_acceptable_next_terminals(partial_code)
    print(next_ac_terminals)
    assert 'FLOAT_NUMBER' in next_ac_terminals

def test_parser3():
    inc_parser = IncrementalParser()
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t\n\tfor i in range(len(numbers) -1, -1, -1) :\n\t\tfor j in range(i+1, len(numbers) ,1) :\n\t\t\tif abs(numbers[i] - numbers[j] ) < threshold :\n\t\t\t\treturn True\n'
    _, next_ac_terminals, _ = inc_parser.get_acceptable_next_terminals(partial_code)
    assert '_TAB' in next_ac_terminals

def test_parser4():
    inc_parser = IncrementalParser()
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t\n\tfor i in range(len(numbers) -1, -1, -1) :\n\t\tfor j in range(i+1, len(numbers) ,1) :\n\t\t\tif abs(numbers[i] - numbers[j] ) < threshold :\n'
    _, next_ac_terminals, _ = inc_parser.get_acceptable_next_terminals(partial_code)
    assert '_TAB' in next_ac_terminals

def test_parser5():
    inc_parser = IncrementalParser()
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t\n\tfor i in range(len(numbers) -1, -1, -1) :\n\t\tfor j in range(i+1, len(numbers) ,1) :\n\t\t\tif abs(numbers[i] - numbers[j] ) < threshold :\n\t\t\t\treturn True\n\t\t\t\t'
    # There cannot be another tab after this
    _, next_ac_terminals, _ = inc_parser.get_acceptable_next_terminals(partial_code)
    assert '_TAB' not in next_ac_terminals

def test_parser6():
    inc_parser = IncrementalParser()
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t\n\tfor i in range(len(numbers) -1, -1, -1) :\n\t\tfor j in range(i+1, len(numbers) ,1) :\n\t\t\tif abs(numbers[i] - numbers[j] ) < threshold :\n\t\t\t\treturn True\n\n\n\t\t\t\t'
    # There cannot be another tab after this
    _, next_ac_terminals, _ = inc_parser.get_acceptable_next_terminals(partial_code)
    assert '_TAB' not in next_ac_terminals

def test_parser6():
    inc_parser = IncrementalParser()
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t\n\tfor i in range(len(numbers) -1, -1, -1) :\n\t\tfor j in range(i+1, len(numbers) ,1) :\n\t\t\tif abs(numbers[i] - numbers[j] ) < threshold :\n\t\t\t\treturn True\n\n\t\t\t\n\t\t'
    # There can be another tab after this
    _, next_ac_terminals, _ = inc_parser.get_acceptable_next_terminals(partial_code)
    assert '_TAB' in next_ac_terminals

def test_parser7():
    inc_parser = IncrementalParser()
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\tfor i in range(len(numbers) -1, -1, -1) :\n\t\tif numbers[i] - numbers[i+1] < threshold:\n\t\t\treturn True\n\treturn False\n'
    _, next_ac_terminals, _ = inc_parser.get_acceptable_next_terminals(partial_code)
    assert '_TAB' in next_ac_terminals
    assert '_NL' in next_ac_terminals

def test_parser8():
    inc_parser = IncrementalParser()
    partial_code = 'from typing import List\n\n\ndef separate_paren_groups(paren_string: str) -> List[str]:\n\tpar = []\n\tfor i in par:\n\t\tif i == \''
    _, next_ac_terminals, cur_term_str = inc_parser.get_acceptable_next_terminals(partial_code)
    assert cur_term_str == " '"

def test_parser9():
    inc_parser = IncrementalParser()
    partial_code = 'from typing import List\n\n\ndef separate_paren_groups(paren_string: str) -> List[str]:\n\tpar = []\n\tfor i in par:\n\t\tif i == \'Hello'
    _, next_ac_terminals, cur_term_str = inc_parser.get_acceptable_next_terminals(partial_code)
    print(cur_term_str)
    assert cur_term_str == " 'Hello"

def test_parser10():
    inc_parser = IncrementalParser()
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t""" Check if in given list of numbers, are any two numbers closer to each other than\n\tgiven threshold.\n\t>>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n\tFalse\n\t>>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n\tTrue\n\t"""\n\tfor i in range(len(numbers) -1, -1, -1):\n\t\tfor j in range(i+1, len(numbers) -1, -1):\n\t\t\tif abs(numbers[i] - numbers[j] ) < threshold:\n\t\t\t\treturn True\n\treturn False\n\n\ndef has_close_elements_with_threshold(numbers: List[float] , threshold: float) -> bool:\n\t""'
    cur_ac_terminals, next_ac_terminals, cur_term_str = inc_parser.get_acceptable_next_terminals(partial_code)
    assert cur_term_str == '""'

def test_parser11():
    inc_parser = IncrementalParser()
    partial_codes = ['from typing import List, Tuple\n\n\ndef rolling_max(numbers: List[int]) -> List[int]:\n\t""" From a given list of integers, generate a list of rolling maximum element found until given moment\n\tin the sequence.\n\t>>> rolling_max([1, 2, 3, 2, 3, 4, 2])\n\t[1, 2, 3, 3, 3, 4, 4]\n\t"""\n\tresult = []\n\tfor i in range(len(numbers)):\n\t\tif i == len(numbers) - 1:  # if we are at the end of the sequence\n\t\t\tresult.append(numbers[i]) ']
    cur_ac_terminals, next_ac_terminals, cur_term_str = inc_parser.get_acceptable_next_terminals(partial_codes[-1])
    should_not_contain = inc_parser.get_prefix_terminals_match('//')
    print(next_ac_terminals)
    print(should_not_contain)
    assert 'COMMENT' in next_ac_terminals

def test_parser12(): 
    inc_parser = IncrementalParser()
    partial_code = 'from typing import List\n\n\ndef rescale_to_unit(numbers: List[float]) -> List[float]:\n\t""" Given list of numbers (of at least two elements), apply a linear transform to that list,\n\tsuch that the smallest number will become 0 and the largest will become 1\n\t>>> rescale_to_unit([1.0, 2.0, 3.0, 4.0, 5.0])\n\t[0.0, 0.25, 0.5, 0.75, 1.0]\n\t"""\n\tfor i in x: # this is'
    # This should not crash. Earlier version was crashing on this
    _, next_ac_terminals, _ = inc_parser.get_acceptable_next_terminals(partial_code)

def test_incremental_parser():
    inc_parser = IncrementalParser()
    partial_code = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t""" Check if in given list of numbers, are any two numbers closer to each other than\n\tgiven threshold.\n\t>>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n\tFalse\n\t>>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n\tTrue\n\t"""\n\tfor i in range(len(numbers) -1, -1, -1):\n\t\tfor j in range(i+1, len(numbers) -1, -1):\n\t\t\tif abs(numbers[i] - numbers[j] ) < threshold:\n\t\t\t\treturn True\n\treturn False\n\n\ndef has_close_elements_with_threshold(numbers: List[float] , threshold: float) -> bool:\n\t""'
    cur_ac_terminals, next_ac_terminals, cur_term_str = inc_parser.get_acceptable_next_terminals(partial_code[:len(partial_code)-10])
    cur_ac_terminals, next_ac_terminals, cur_term_str = inc_parser.get_acceptable_next_terminals(partial_code)
    assert cur_term_str == '""'

def test_incremental_parser2():
    inc_parser = IncrementalParser()
    prompt = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t""" Check if in given list of numbers, are any two numbers closer to each other than\n\tgiven threshold.\n\t>>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n\tFalse\n\t>>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n\tTrue\n'

    generated_code = '\t"""\n\tfor i in range(len(numbers) -1, -1, -1):\n\t\tfor j in range(i+1, len(numbers) -1, -1):\n\t\t\tif abs(numbers[i] - numbers[j] ) < threshold:\n\t\t\t\treturn True\n\treturn False\n\n\ndef has_close_elements_with_threshold(numbers: List[float] , threshold: float) -> bool:\n\ta="shu'

    i = 0
    while i<len(generated_code):
        i += 2
        _, _, cur_term_str = inc_parser.get_acceptable_next_terminals(prompt + generated_code[:i])
    assert cur_term_str == '"shu'

def test_incremental_parser3():
    inc_parser = IncrementalParser()
    partial_codes = ['from typing import List\n\n\ndef rescale_to_unit(numbers: List[float]) -> List[float]:\n\t""" Given list of numbers (of at least two elements), apply a linear transform to that list,\n\tsuch that the smallest number will become 0 and the largest will become 1\n\t>>> rescale_to_unit([1.0, 2.0, 3.0, 4.0, 5.0])\n\t[0.0, 0.25, 0.5, 0.75, 1.0]\n\t"""\n\tmin_num = min(numbers)\n\tmax_num = max(numbers)\n\treturn [min_num * (x - min_num) / (max_num - min_num) + min_num for x in numbers]\n\n', 'from typing import List\n\n\ndef rescale_to_unit(numbers: List[float]) -> List[float]:\n\t""" Given list of numbers (of at least two elements), apply a linear transform to that list,\n\tsuch that the smallest number will become 0 and the largest will become 1\n\t>>> rescale_to_unit([1.0, 2.0, 3.0, 4.0, 5.0])\n\t[0.0, 0.25, 0.5, 0.75, 1.0]\n\t"""\n\tmin_num = min(numbers)\n\tmax_num = max(numbers)\n\treturn [min_num * (x - min_num) / (max_num - min_num) + min_num for x in numbers]\n\n\n', 'from typing import List\n\n\ndef rescale_to_unit(numbers: List[float]) -> List[float]:\n\t""" Given list of numbers (of at least two elements), apply a linear transform to that list,\n\tsuch that the smallest number will become 0 and the largest will become 1\n\t>>> rescale_to_unit([1.0, 2.0, 3.0, 4.0, 5.0])\n\t[0.0, 0.25, 0.5, 0.75, 1.0]\n\t"""\n\tmin_num = min(numbers)\n\tmax_num = max(numbers)\n\treturn [min_num * (x - min_num) / (max_num - min_num) + min_num for x in numbers]\n\n\ndef']
    for i, partial_code in enumerate(partial_codes):
        new_inc_parser = IncrementalParser()
        cur_ac_terminals, next_ac_terminals, cur_term_str = inc_parser.get_acceptable_next_terminals(partial_code)
        cur_ac_terminals2, next_ac_terminals2, cur_term_str2 = new_inc_parser.get_acceptable_next_terminals(partial_code)
        
        assert next_ac_terminals == next_ac_terminals2

def test_incremental_parser4():
    inc_parser = IncrementalParser()
    partial_codes = ['\n\ndef derivative(xs: list):\n\t""" xs represent coefficients of a polynomial.\n\txs[0] + xs[1] * x + xs[2] * x^2 + ....\n\t Return derivative of this polynomial in the same form.\n\t>>> derivative([3, 1, 2, 4, 5])\n\t[1, 4, 12, 20]\n\t>>> derivative([1, 2, 3])\n\t[2, 6]\n\t"""\n\txs = list(xs)', '\n\ndef derivative(xs: list):\n\t""" xs represent coefficients of a polynomial.\n\txs[0] + xs[1] * x + xs[2] * x^2 + ....\n\t Return derivative of this polynomial in the same form.\n\t>>> derivative([3, 1, 2, 4, 5])\n\t[1, 4, 12, 20]\n\t>>> derivative([1, 2, 3])\n\t[2, 6]\n\t"""\n\txs = list(xs)\n', '\n\ndef derivative(xs: list):\n\t""" xs represent coefficients of a polynomial.\n\txs[0] + xs[1] * x + xs[2] * x^2 + ....\n\t Return derivative of this polynomial in the same form.\n\t>>> derivative([3, 1, 2, 4, 5])\n\t[1, 4, 12, 20]\n\t>>> derivative([1, 2, 3])\n\t[2, 6]\n\t"""\n\txs = list(xs)\n\t']
    for i, partial_code in enumerate(partial_codes):
        new_inc_parser = IncrementalParser()
        cur_ac_terminals, next_ac_terminals, cur_term_str = inc_parser.get_acceptable_next_terminals(partial_code)
        cur_ac_terminals2, next_ac_terminals2, cur_term_str2 = new_inc_parser.get_acceptable_next_terminals(partial_code)
        print(next_ac_terminals)
        assert next_ac_terminals == next_ac_terminals2, i 

def test_get_matching_terminals():
    inc_parser = IncrementalParser()
    assert inc_parser.get_matching_terminal("\t") == "_TAB"
    # assert inc_parser.get_matching_terminal(tokenizer.decode(torch.tensor([12]), skip_special_tokens=True)) == "_TAB"
    
    assert inc_parser.get_matching_terminal("\n") == "_NL"
    # assert inc_parser.get_matching_terminal(tokenizer.decode(torch.tensor([13]), skip_special_tokens=True)) == "_NL"
    
    # Keywords
    assert inc_parser.get_matching_terminal("def") == "DEF"
    assert inc_parser.get_matching_terminal("in") == "IN"
    assert inc_parser.get_matching_terminal("if") == "IF"
    assert inc_parser.get_matching_terminal("else") == "ELSE"
    assert inc_parser.get_matching_terminal("elif") == "ELIF"
    assert inc_parser.get_matching_terminal("for") == "FOR"
    assert inc_parser.get_matching_terminal("while") == "WHILE"
    assert inc_parser.get_matching_terminal("try") == "TRY"
    assert inc_parser.get_matching_terminal("except") == "EXCEPT"
    assert inc_parser.get_matching_terminal("finally") == "FINALLY"
    assert inc_parser.get_matching_terminal("with") == "WITH"
    assert inc_parser.get_matching_terminal("class") == "CLASS"

    # Regex
    assert inc_parser.get_matching_terminal("1234") == "DEC_NUMBER"
    assert inc_parser.get_matching_terminal("12.34") == "FLOAT_NUMBER"
    assert inc_parser.get_matching_terminal("pqr") == "NAME"
    assert inc_parser.get_matching_terminal("\'ssss\'") == "STRING"
    assert inc_parser.get_matching_terminal('\"ssss\"') == "STRING"
    assert inc_parser.get_matching_terminal('\"""ssss\"""') == "COMMENT"
    assert inc_parser.get_matching_terminal('\"""ssss') == None

def test_prefix_terminal_match():
    inc_parser = IncrementalParser()
    # Check if the string can be prefix to the Regex
    assert "DEF" in inc_parser.get_prefix_terminals_match("de") 
    assert "DEF" in inc_parser.get_prefix_terminals_match("d")
    assert "DEF" in inc_parser.get_prefix_terminals_match("def")
    assert "LPAR" in inc_parser.get_prefix_terminals_match("(")
    assert "RPAR" in inc_parser.get_prefix_terminals_match(")")
    assert "STRING" in inc_parser.get_prefix_terminals_match("'")
    assert "STRING" in inc_parser.get_prefix_terminals_match("''")
    assert "LONG_STRING" in inc_parser.get_prefix_terminals_match('"')
    assert "LONG_STRING" in inc_parser.get_prefix_terminals_match('""')
    assert "LONG_STRING" in inc_parser.get_prefix_terminals_match('"""')
    assert "LONG_STRING" in inc_parser.get_prefix_terminals_match('"""" something')
    assert "COMMENT" in inc_parser.get_prefix_terminals_match('"""')
    assert "COMMENT" in inc_parser.get_prefix_terminals_match('""" something')
    assert "COMMENT" in inc_parser.get_prefix_terminals_match('# something')

    assert not "RPAR" in inc_parser.get_prefix_terminals_match("(")


tests = [test_get_matching_terminals, test_parser1, test_parser2, test_parser3, test_parser4, test_parser5, test_parser6, test_parser7, test_parser8, test_parser9, test_parser10, test_parser11, test_parser12,test_incremental_parser, test_incremental_parser2, test_incremental_parser3, test_incremental_parser4, test_prefix_terminal_match]

run_tests(tests)
