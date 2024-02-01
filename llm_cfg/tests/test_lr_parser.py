import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')

from incremental_parser import IncrementalParser
from common import run_tests
from parse_result import RemainderState

def test_tiny():
    inc_parser = IncrementalParser('llm_cfg/grammars/tiny_grammar.lark', parser='lr')
    partial_code = "ccdd"
    out = inc_parser.parser.parse(partial_code)
    print(out)

def test_calc():
    inc_parser = IncrementalParser('llm_cfg/grammars/calc_grammar.lark', parser='lr')
    partial_code = "113 + 235 + 17"
    out = inc_parser.parser.parse(partial_code)
    assert out.children[0].children[0].children[1].children[0] == '235'

run_tests([test_calc, test_tiny]) 
