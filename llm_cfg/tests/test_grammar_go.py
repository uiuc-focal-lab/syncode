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

def test_incremental_go_parser():
    inc_parser = GoIncrementalParser()
    partial_code = f'''package main
import "fmt"
func main() {{
  var x int = 10
  var y int ='''
    out = inc_parser._lex_code(partial_code)
    assert out[-1].type == 'EQUAL'

tests = [test_go_parser, test_go_parser2, test_go_parser3, test_incremental_go_parser]
run_tests(tests)
