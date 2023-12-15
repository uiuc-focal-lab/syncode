import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from grammars.go_parser import GoIncrementalParser
from common import run_tests
from transformers import (
    LlamaTokenizer,
)
from parse_result import RemainderState

def test_tree_printer():
    '''
    NOTE: The EOS ignoring is handled seperately in Go incremental parser. Just calling the standard lark parser for printing the tree will not ignore EOS.
    '''
    inc_parser = GoIncrementalParser()
    partial_code = f'''package main
    import "fmt"
func main() {{
  a = x.fun(num[i], 7);}}
  '''
    # partial_code = 'package main\n\nfunc has_close_elements (numbers []float64, threshold float64) bool {\n\tvar (\t\tmin, max float64\n\t\tmin_index, max_index int\n\t)\n\tfor i, n := range 5 {\na=i\n}\n};'
    t = inc_parser.parser.parse(partial_code)
    print(t.pretty())

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

def test_parser2():
    inc_parser = GoIncrementalParser()
    partial_code = 'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\n// You\'re an expert Golang programmer\n// Check if in given list of numbers, are any two numbers closer to each other than\n// given threshold.\n// >>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n// False\n// >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n// True\n// \nfunc has_close_elements (numbers []float64, threshold float64) bool {\n' 
    print(partial_code)
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    print(res)

def test_go_parser():
    inc_parser = GoIncrementalParser()
    code = f'''package main
import "fmt"
func main() {{
    a, b = 3, 5
}}
'''
    out = inc_parser.parser.parse(code)
    print(out.pretty())

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

def test_go_parser4():
    inc_parser = GoIncrementalParser()
    partial_code =  'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\n// You\'re an expert Golang programmer\n// Check if in given list of numbers, are any two numbers closer to each other than\n// given threshold.\n// >>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n// False\n// >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n// True\n// \nfunc has_close_elements (numbers []float64, threshold float64) bool {\n\n  // 1. ' 
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    assert '\n\n  // 1. ' == res.remainder

def test_go_parser5():
    inc_parser = GoIncrementalParser()
    partial_code = 'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\n// You\'re an expert Golang programmer\n// Return a string containing space-delimited numbers starting from 0 upto n inclusive.\n// >>> string_sequence(0)\n// \'0\'\n// >>> string_sequence(5)\n// \'0 1 2 3 4 5\'\n// \nfunc string_sequence (n int) string {\n\tvar result string\n\tfor i := 0; i < n; i++ {\n\t\tresult += strconv.Itoa(i'
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    assert res.remainder == 'i'

def test_go_parser6():
    inc_parser = GoIncrementalParser()
    partial_code = 'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\n// You\'re an expert Golang programmer\n// Insert a number \'delimeter\' between every two consecutive elements of input list `numbers\'\n// >>> intersperse([], 4)\n// []\n// >>> intersperse([1, 2, 3], 4)\n// [1, 4, 2, 4, 3]\n// \nfunc intersperse (numbers []int, delimeter int) []int {\n\tvar (  i, j int\n\t\tk int\n\t\tl []int\n\t)\n\tfor i = 0; i < len(numbers); i++ {\n\t\tfor j = i + 1; j < len(numbers); j++ {\n\t\t\tk = numbers[i] + delimeter + numbers[j]\n\t\t\tl = append(l, k)\n\t\t}\n\t}\n\treturn l\n}\n\nfunc main() {\n\t// Get the JSON string from the URL\n\tvar (  url string\n\t\tjsonData string\n\t\terr error\n\t)\n\turl = "http://localhost:8080/api/v1/json/get_data"\n\tjsonData, err '
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    assert 'EQUAL' in res.next_accept_terminals

def test_go_parser7():
    inc_parser = GoIncrementalParser()
    partial_code = 'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\n// You\'re an expert Golang programmer\n// Insert a number \'delimeter\' between every two consecutive elements of input list `numbers\'\n// >>> intersperse([], 4)\n// []\n// >>> intersperse([1, 2, 3], 4)\n// [1, 4, 2, 4, 3]\n// \nfunc intersperse (numbers []int, delimeter int) []int {\n\tvar (\n'
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    assert '__IGNORE_1' in res.next_accept_terminals

def test_go_parser8():
    inc_parser = GoIncrementalParser()
    partial_code = 'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\nfunc has_close_elements (numbers []float64, threshold float64) bool {\n\tif threshold > numbers[len(numbers)/'
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    assert 'DECIMAL_LIT' in res.next_accept_terminals

def test_go_parser9():
    inc_parser = GoIncrementalParser()
    partial_code = 'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\nfunc has_close_elements (numbers []float64, threshold float64) bool {\n\tvar (\n\t\tmin, max float64\n\t\tmin_index, max_index int\n\t)\n\tfor i, n := range numbers'
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    assert 'LBRACE' in res.next_accept_terminals

def test_go_parser10():
    inc_parser = GoIncrementalParser()
    partial_code = 'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\nfunc has_close_elements (numbers []float64, threshold float64) bool { x:= 1; '
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    assert 'EOF' in res.next_accept_terminals

def test_go_parser11():
    inc_parser = GoIncrementalParser()
    partial_code =  'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\n// You\'re an expert Golang programmer\n// Check if in given list of numbers, are any two numbers closer to each other than\n// given threshold.\n// >>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n// False\n// >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n// True\n// \nfunc has_close_elements (numbers []float64, threshold float64) bool {\n\tif len(numbers) < 2 {\n\t\treturn false\n\t}\n\n\tfor i := 0; i < len(numbers)-1; i++ {\n\t\tfor j := i + 1; j < len(numbers); j++ {\n\t\t\tif reflect.DeepEqual(numbers[i],'
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    assert 'DECIMAL_LIT' in res.next_accept_terminals

def test_go_incremental_parser():
    inc_parser = GoIncrementalParser()
    partial_code =  'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\nfunc truncate_number (number float64) float64 {\n\tvar ('
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    partial_code =  'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\nfunc truncate_number (number float64) float64 {\n\tvar (\n\t\tint_part float'
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    assert 'NAME' in res.cur_accept_terminals

def test_go_incremental_parser2():
    inc_parser = GoIncrementalParser()
    prompt = 'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\n'
    generated_code = 'func truncate_number (number float64) float64 {\n\tvar (\n\n\t\tinteger_part float'

    i = 0
    while i<len(generated_code):
        i += 2
        r = inc_parser.get_acceptable_next_terminals(prompt + generated_code[:i])
    assert r.remainder == 'float'

tests = [test_go_parser, test_go_parser2, test_go_parser3, test_go_parser4, test_go_parser5, test_go_parser6, test_go_parser7, test_go_parser8, test_go_parser9, test_go_parser10, test_go_parser11, test_lexer, test_interactive_parser, test_go_incremental_parser, test_go_incremental_parser2]
# tests = [test_tree_printer]
run_tests(tests)
