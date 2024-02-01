import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')

from incremental_parser import IncrementalParser
from common import run_tests

def test_tiny():
    inc_parser = IncrementalParser('llm_cfg/grammars/tiny_grammar.lark', parser='lr')
    partial_code = "ccdd"
    out = inc_parser.parser.parse(partial_code)
    print(out)

def test_calc():
    # 17 states become 31 from LALR(1) to LR(1)
    inc_parser = IncrementalParser('llm_cfg/grammars/calc_grammar.lark', parser='lr')
    partial_code = "113 + 235 + 1111"
    out = inc_parser.parser.parse(partial_code)
    assert out.children[0].children[0].children[1].children[0] == '235'

def test_python_size():
    # 752 states become 4926 from LALR(1) to LR(1)
    inc_parser = IncrementalParser('llm_cfg/grammars/python_grammar.lark', parser='lr')
    print(len(inc_parser.parser.parser.parser._parse_table.states))

# Not adding test_python_size as it may take about 3-4 minutes to run
tests = [test_calc, test_tiny]
run_tests(tests) 
