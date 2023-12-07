import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from grammars.php_parser import PhpIncrementalParser
from common import run_tests
from parse_result import RemainderState

def test_lexer():
    inc_parser = PhpIncrementalParser()
    partial_code = "<?php\n\n/**\n * You are an expert PHP programmer, and here is your task.\n * Check if in given list of numbers, are any two numbers closer to each other than\n * given threshold.\n * >>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n * False\n * >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n * True\n *\n */\nfunction hasCloseElements($numbers, $threshold){\n"
    out = inc_parser._lex_code(partial_code)
    print(out)

run_tests([test_lexer]) 
