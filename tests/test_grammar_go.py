import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from syncode.common import run_tests
from syncode.parse_result import AcceptSequence, RemainderState
from syncode.parsers import create_parser
from syncode.parsers.grammars import Grammar

go_grammar = Grammar('go')
inc_parser = create_parser(go_grammar)

def test_tree_printer():
    '''
    NOTE: The EOS ignoring is handled seperately in Go incremental parser. Just calling the standard lark parser for printing the tree will not ignore EOS.
    '''
    inc_parser.reset()
    partial_code = f'''package main
    import "fmt"
func main() {{
  //a = x.fun(num[i], 7);
  //t(p.q.r)
  x := y.(z)
  }}
  '''
    # partial_code = 'package main\n\nfunc has_close_elements (numbers []float64, threshold float64) bool {\n\tvar (\t\tmin, max float64\n\t\tmin_index, max_index int\n\t)\n\tfor i, n := range 5 {\na=i\n}\n};'
    t = inc_parser.base_parser.parse(partial_code)
    print(t.pretty())

def test_lexer():
    inc_parser.reset()
    partial_code = f'''package main
import "fmt"
func main() {{
  var x int = 10
  var y int ='''
    out = inc_parser._lex_code(partial_code)
    assert out[-1].type == 'EQUAL'

def test_interactive_parser():
    inc_parser.reset()
    partial_code = f'''package main
import "fmt"
func main() {{
  var x int = 10
  var y int ='''
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    assert AcceptSequence(['EQUAL', 'DECIMAL_LIT']) in res.accept_sequences

def test_parser2():
    inc_parser.reset()
    partial_code = 'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\n// You\'re an expert Golang programmer\n// Check if in given list of numbers, are any two numbers closer to each other than\n// given threshold.\n// >>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n// False\n// >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n// True\n// \nfunc has_close_elements (numbers []float64, threshold float64) bool {\n' 
    print(partial_code)
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    print(res)

def test_go_parser():
    inc_parser.reset()
    code = f'''package main
import "fmt"
func main() {{
    a, b = 3, 5
}}
'''
    out = inc_parser.base_parser.parse(code)
    print(out.pretty())

def test_go_parser2():
    inc_parser.reset()
    code = f'''package main

import "fmt"

func main() {{
  var x int = 10
  var y int = 20
  var z int = x + y
  fmt.Println(z)
}}
'''
    out = inc_parser.base_parser.parse(code)

def test_go_parser3():
    failed = False
    inc_parser.reset()
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
        out = inc_parser.base_parser.parse(code)
    except Exception as e:
        failed = True
    assert failed

def test_go_parser4():
    inc_parser.reset()
    partial_code =  'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\n// You\'re an expert Golang programmer\n// Check if in given list of numbers, are any two numbers closer to each other than\n// given threshold.\n// >>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n// False\n// >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n// True\n// \nfunc has_close_elements (numbers []float64, threshold float64) bool {\n\n  // 1. ' 
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    assert '\n\n  // 1. ' == res.remainder

def test_go_parser5():
    inc_parser.reset()
    partial_code = 'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\n// You\'re an expert Golang programmer\n// Return a string containing space-delimited numbers starting from 0 upto n inclusive.\n// >>> string_sequence(0)\n// \'0\'\n// >>> string_sequence(5)\n// \'0 1 2 3 4 5\'\n// \nfunc string_sequence (n int) string {\n\tvar result string\n\tfor i := 0; i < n; i++ {\n\t\tresult += strconv.Itoa(i'
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    assert res.remainder == 'i'

def test_go_parser6():
    inc_parser.reset()
    partial_code = 'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\n// You\'re an expert Golang programmer\n// Insert a number \'delimeter\' between every two consecutive elements of input list `numbers\'\n// >>> intersperse([], 4)\n// []\n// >>> intersperse([1, 2, 3], 4)\n// [1, 4, 2, 4, 3]\n// \nfunc intersperse (numbers []int, delimeter int) []int {\n\tvar (  i, j int\n\t\tk int\n\t\tl []int\n\t)\n\tfor i = 0; i < len(numbers); i++ {\n\t\tfor j = i + 1; j < len(numbers); j++ {\n\t\t\tk = numbers[i] + delimeter + numbers[j]\n\t\t\tl = append(l, k)\n\t\t}\n\t}\n\treturn l\n}\n\nfunc main() {\n\t// Get the JSON string from the URL\n\tvar (  url string\n\t\tjsonData string\n\t\terr error\n\t)\n\turl = "http://localhost:8080/api/v1/json/get_data"\n\tjsonData, err '
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    # assert 'EQUAL' in res.next_accept_terminals
    print(res)
    assert AcceptSequence(['EQUAL']) in res.accept_sequences

def test_go_parser7():
    inc_parser.reset()
    partial_code = 'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\n// You\'re an expert Golang programmer\n// Insert a number \'delimeter\' between every two consecutive elements of input list `numbers\'\n// >>> intersperse([], 4)\n// []\n// >>> intersperse([1, 2, 3], 4)\n// [1, 4, 2, 4, 3]\n// \nfunc intersperse (numbers []int, delimeter int) []int {\n\tvar (\n'
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    # WHY was this added?
    # assert '__IGNORE_1' in res.next_accept_terminals

def test_go_parser8():
    inc_parser.reset()
    partial_code = 'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\nfunc has_close_elements (numbers []float64, threshold float64) bool {\n\tif threshold > numbers[len(numbers)/'
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    assert AcceptSequence(['SLASH', 'DECIMAL_LIT']) in res.accept_sequences
    assert res.remainder == '/'

def test_go_parser9():
    inc_parser.reset()
    partial_code = 'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\nfunc has_close_elements (numbers []float64, threshold float64) bool {\n\tvar (\n\t\tmin, max float64\n\t\tmin_index, max_index int\n\t)\n\tfor i, n := range numbers'
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    assert AcceptSequence(['NAME', 'LBRACE']) in res.accept_sequences

def test_go_parser10():
    inc_parser.reset()
    partial_code = 'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\nfunc has_close_elements (numbers []float64, threshold float64) bool { x:= 1; '
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    assert AcceptSequence(['EOF']) in res.accept_sequences

def test_go_parser11():
    inc_parser.reset()
    partial_code =  'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\n// You\'re an expert Golang programmer\n// Check if in given list of numbers, are any two numbers closer to each other than\n// given threshold.\n// >>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n// False\n// >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n// True\n// \nfunc has_close_elements (numbers []float64, threshold float64) bool {\n\tif len(numbers) < 2 {\n\t\treturn false\n\t}\n\n\tfor i := 0; i < len(numbers)-1; i++ {\n\t\tfor j := i + 1; j < len(numbers); j++ {\n\t\t\tif reflect.DeepEqual(numbers[i],'
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    assert AcceptSequence(['COMMA', 'DECIMAL_LIT']) in res.accept_sequences

def test_go_parser12():
    inc_parser.reset()
    partial_code =   'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\n// You\'re an expert Golang programmer\n// Insert a number \'delimeter\' between every two consecutive elements of input list `numbers\'\n// >>> intersperse([], 4)\n// []\n// >>> intersperse([1, 2, 3], 4)\n// [1, 4, 2, 4, 3]\n// \nfunc intersperse (numbers []int, delimeter int) []int {\n\tresult := make([]int64'
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    assert AcceptSequence(['NAME', 'COMMA']) in res.accept_sequences
    assert res.remainder == 'int64'
    assert res.remainder_state == RemainderState.MAYBE_COMPLETE

def test_go_parser13():
    inc_parser.reset()
    partial_code = 'package main\n\nimport (\n\t"math"\n\t"encoding/json"\n\t"reflect"\n)\n// You\'re an expert Golang programmer\n// Return list of prime factors of given integer in the order from smallest to largest.\n// Each of the factors should be listed number of times corresponding to how many times it appeares in factorization.\n// Input number should be equal to the product of all factors\n// >>> factorize(8)\n// [2, 2, 2]\n// >>> factorize(25)\n// [5, 5]\n// >>> factorize(70)\n// [2, 5, 7]\n// \nfunc factorize (n int) []int {\n\tfactors := make([]int, 0)\n\tfor i := 2; i <= int(math.Sqrtln'
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    # assert 'LPAR' in res.next_accept_terminals
    assert AcceptSequence(['NAME', 'LPAR']) in res.accept_sequences
    assert res.remainder == 'Sqrtln'
    assert res.remainder_state == RemainderState.MAYBE_COMPLETE

def test_go_parser14():
    inc_parser.reset()
    partial_code = 'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\n// You\'re an expert Golang programmer\n// Out of list of strings, return the longest one. Return the first one in case of multiple\n// strings of the same length. Return None in case the input list is empty.\n// >>> longest([])\n// \n// >>> longest([\'a\', \'b\', \'c\'])\n// \'a\'\n// >>> longest([\'a\', \'bb\', \'ccc\'])\n// \'ccc\'\n// \nfunc longest (strings []string) interface{} {\n\t'
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    print(res)
    assert AcceptSequence(['EOS', 'IF']) in res.accept_sequences

def test_go_parser15():
    inc_parser.reset()
    partial_code =  'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\nfunc numerical_letter_grade (grades []interface{}) []string {\n\tletter_grades := make([]string, len(grades))\n\tfor i, grade := range grades {\n\t\tswitch grade.('
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    assert AcceptSequence(['LPAR', 'TYPE']) in res.accept_sequences
    assert AcceptSequence(['LPAR', '__IGNORE_0']) in res.accept_sequences

def test_go_parser16():
    inc_parser.reset()
    partial_code = 'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\nfunc hex_key (num interface{}) int {\n\tvar hex_digits = []string{"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"}\n\tvar hex_count int\n\tvar hex_primes []int\n\tvar hex_prime_count int\n\tvar hex_prime_count_map = make(map[int]int)\n\n\t// Convert hexadecimal number to int\n\thex_num, ok := num.(string'
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    assert AcceptSequence(['NAME', 'RPAR']) in res.accept_sequences  

def test_go_incremental_parser():
    inc_parser.reset()
    partial_code =  'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\nfunc truncate_number (number float64) float64 {\n\tvar ('
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    partial_code =  'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\nfunc truncate_number (number float64) float64 {\n\tvar (\n\t\tint_part float'
    res = inc_parser.get_acceptable_next_terminals(partial_code)
    print(res)
    assert AcceptSequence(['NAME', 'EOS']) in res.accept_sequences

def test_go_incremental_parser2():
    inc_parser.reset()
    prompt = 'package main\n\nimport (\n\t"encoding/json"\n\t"reflect"\n)\n'
    generated_code = 'func truncate_number (number float64) float64 {\n\tvar (\n\n\t\tinteger_part float'

    i = 0
    while i<len(generated_code):
        i += 2
        r = inc_parser.get_acceptable_next_terminals(prompt + generated_code[:i])
    assert r.remainder == 'float'

tests = [test_go_parser, test_go_parser2, test_go_parser3, test_go_parser4, test_go_parser5, test_go_parser6, test_go_parser8, test_go_parser9, test_go_parser10, test_go_parser11, test_go_parser12, test_go_parser13, test_go_parser14, test_go_parser15, test_go_parser16, test_lexer, test_interactive_parser, test_go_incremental_parser, test_go_incremental_parser2]
# tests = [test_tree_printer]
# tests = [test_go_parser17]
run_tests(tests)
