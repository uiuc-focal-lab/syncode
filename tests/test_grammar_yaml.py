import unittest
import os
import sys

# Adjusting the path so the modules can be imported correctly
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')

from syncode.parsers import create_parser
from syncode.parse_result import AcceptSequence
from syncode.parsers.grammars.grammar import Grammar

class TestYamlParser(unittest.TestCase):
    def test_grammar_yaml(self):
        yaml_grammar = Grammar('yaml')
        inc_parser = create_parser(yaml_grammar, parser='lr', use_cache=False)
        partial_code = """sea: false
place: false
at:
  learn: story
  face: near
  location: 1975375703
  method: better
  region:
    - sent
    - true
    - 169398512
    - end
    - -1906668625.3438973
    - -1651080621
  property: compound
series: 1717816454.9481492
population: -1416707999
complex: throughout
"""     
        t = inc_parser.base_parser.parse(partial_code)
        print(t.pretty())
        # r = inc_parser.get_acceptable_next_terminals(partial_code)
        

    def test_parser1(self):
        inc_parser = create_parser(Grammar('yaml'), parser='lr', use_cache=False)
        partial_code = " Use"
        r = inc_parser.get_acceptable_next_terminals(partial_code)
        print(r)
        # self.assertEqual(r.remainder, 'value')
        