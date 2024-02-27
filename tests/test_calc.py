import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from syncode.parsers import create_parser
from syncode.common import run_tests
from syncode.parse_result import AcceptSequence
from syncode.parsers.grammars.grammar import Grammar


def test_parser():
    inc_parser = create_parser(Grammar('calc'))
    partial_code = "113 + 235 + 17"
    r = inc_parser.get_acceptable_next_terminals(partial_code)
    assert r.remainder == '17'
    assert AcceptSequence(['NUMBER', 'PLUS']) in r.accept_sequences
    assert AcceptSequence(['NUMBER', 'STAR']) in r.accept_sequences
    assert AcceptSequence(['LPAR']) in r.accept_sequences

def test_parser2():
    inc_parser = create_parser(Grammar('calc'))
    partial_code = "11333"
    r = inc_parser.get_acceptable_next_terminals(partial_code)
    assert r.remainder == '11333'
    assert AcceptSequence(['NUMBER', 'PLUS']) in r.accept_sequences

run_tests([test_parser, test_parser2]) 
