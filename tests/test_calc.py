import unittest
import os
import sys

# Adjusting the path so the modules can be imported correctly
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')

from syncode.parsers import create_parser
from syncode.parse_result import AcceptSequence
from syncode.parsers.grammars.grammar import Grammar

class TestCalcParser(unittest.TestCase):
    def test_parser(self):
        inc_parser = create_parser(Grammar('calc'))
        partial_code = "113 + 235 + 17"
        r = inc_parser.get_acceptable_next_terminals(partial_code)
        self.assertEqual(r.remainder, '17')
        self.assertIn(AcceptSequence(['NUMBER', 'PLUS']), r.accept_sequences)
        self.assertIn(AcceptSequence(['NUMBER', 'STAR']), r.accept_sequences)
        self.assertIn(AcceptSequence(['LPAR']), r.accept_sequences)

    def test_parser2(self):
        inc_parser = create_parser(Grammar('calc'))
        partial_code = "11333"
        r = inc_parser.get_acceptable_next_terminals(partial_code)
        self.assertEqual(r.remainder, '11333')
        self.assertIn(AcceptSequence(['NUMBER', 'PLUS']), r.accept_sequences)

