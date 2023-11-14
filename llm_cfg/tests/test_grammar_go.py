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
    print(out)

tests = [test_go_parser]
run_tests(tests)
