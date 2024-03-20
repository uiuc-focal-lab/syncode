import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from syncode.parsers import create_parser
from syncode.parsers.grammars.grammar import Grammar
from syncode.parse_result import AcceptSequence, RemainderState

sql_grammar = Grammar('json')
inc_parser = create_parser(sql_grammar)

class TestJSONParser(unittest.TestCase):
    def test_json_parser1(self):
        # Tests when the last incomplete word is unparsed
        inc_parser.reset()
        partial_code = '{\n  "/'
        r = inc_parser.get_acceptable_next_terminals(partial_code)
        assert r.remainder == '"/'
        assert r.remainder_state == RemainderState.INCOMPLETE
    
    def test_json_parser2(self):
        # Tests when the last incomplete word is unparsed
        inc_parser.reset()
        partial_code = '{\n'
        r = inc_parser.get_acceptable_next_terminals(partial_code)
        assert r.remainder == ''
        assert r.remainder_state == RemainderState.COMPLETE
        