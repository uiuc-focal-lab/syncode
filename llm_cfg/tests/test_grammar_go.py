import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from grammars.go_parser import GoIncrementalParser
from common import run_tests
from transformers import (
    LlamaTokenizer,
)
from parse_result import RemainderState

def test_go_parser():
    inc_parser = GoIncrementalParser()
    code = f'''package main
import "fmt"
func main() {{
    fmt.Println("hello world")
}}
'''
    out = inc_parser.parser.parse(code)

def test_go_parser2():
    inc_parser = GoIncrementalParser()
    code = f'''package main

import "fmt"

func main() {{
  var x int = 10
  var y int = 20
  var z int = x + y
  fmt.Println(z)
}}
'''
    out = inc_parser.parser.parse(code)

def test_go_parser3():
    failed = False
    inc_parser = GoIncrementalParser()
    try:
        code = f'''package main
import "fmt"

func main() {{
  var x int = 10
  var y int =
  var z int = x + y
  fmt.Println(z)
}}
''' 
        out = inc_parser.parser.parse(code)
    except Exception as e:
        failed = True
    assert failed

def test_lexer():
    inc_parser = GoIncrementalParser()
    partial_code = f'''package main
import "fmt"
func main() {{
  var x int = 10
  var y int ='''
    out = inc_parser._lex_code(partial_code)
    assert out[-1].type == 'EQUAL'

def test_interactive_parser():
    inc_parser = GoIncrementalParser()
    partial_code = f'''package main
import "fmt"
func main() {{
  var x int = 10
  var y int ='''
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    assert 'DECIMAL_LIT' in res.next_accept_terminals

def test_interactive_parser2():
    inc_parser = GoIncrementalParser()
    partial_code = 'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\n// You\'re an expert Golang programmer\n// Check if in given list of numbers, are any two numbers closer to each other than\n// given threshold.\n// >>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n// False\n// >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n// True\n// \nfunc has_close_elements (numbers []float64, threshold float64) bool {\n' 
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    print(res)


tests = [test_go_parser, test_go_parser2, test_go_parser3, test_lexer, test_interactive_parser, test_interactive_parser2]
run_tests(tests)
