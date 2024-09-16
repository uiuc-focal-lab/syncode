import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from syncode.parsers import create_parser
from syncode.parsers.grammars.grammar import Grammar
from syncode.parse_result import AcceptSequence, RemainderState

sql_grammar = Grammar('../loopy_expts/invariants.lark')
inc_parser = create_parser(sql_grammar)
inc_parser.reset()
partial_code = "/*@ loop invariant x > 1; */"
r = inc_parser.base_parser.parse(partial_code)
print(r)