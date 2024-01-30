import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')

from incremental_parser import IncrementalParser
from common import run_tests
from parse_result import RemainderState

def test_parser():
    inc_parser = IncrementalParser('llm_cfg/grammars/calc_grammar.lark')
    partial_code = "113 + 235 + 17"
    out = inc_parser.get_acceptable_next_terminals(partial_code)
    print(out)

run_tests([test_parser]) 
