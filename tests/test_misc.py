import unittest
import os
import sys

from syncode.dfa_mask_store import DFAMaskStore

# Adjusting the path so the modules can be imported correctly
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')

from syncode import common
from syncode.parsers import create_parser
from syncode.parse_result import AcceptSequence
from syncode.parsers.grammars.grammar import Grammar

class TestParserMisc(unittest.TestCase):
    @staticmethod
    def math_grammar():
        return """
        start: NUMBER OPERATOR NUMBER "=" NUMBER
        NUMBER: /[0-9]+/
        OPERATOR: "+" | "-" | "*" | "/"

        %ignore " "
    """

    def test_mask_store_misc(self):
        grammar = Grammar(TestParserMisc.math_grammar())
        model = 'microsoft/Phi-3-mini-128k-instruct'
        tokenizer = common.load_tokenizer(model)
        inc_parser = create_parser(grammar)
        r = inc_parser.get_acceptable_next_terminals("234 * 327 = 76518")
        dfa_mask = DFAMaskStore.load_dfa_mask_store(grammar=grammar, tokenizer=tokenizer, use_cache=False, logger=common.EmptyLogger())
        mask = dfa_mask.get_accept_mask(r, get_list=True)
        self.assertNotIn(' (', mask)
    
    @staticmethod
    def essay_grammar():
        # A Lark grammar for paragraphs in text
        return """
        start: paragraph+
        ?paragraph: sentence+
        ?sentence: word+ punctuation
        word: /[a-zA-Z0-9]+/ | COMMA | SINGLE_QUOTE | ESCAPED_DOUBLE_QUOTE
        punctuation: /[.!?]/
        COMMA: ","
        SINGLE_QUOTE: "'"
        ESCAPED_DOUBLE_QUOTE: "\\\""

        %import common.WS
        %ignore WS
    """

    def test_mask_store_misc2(self):
        grammar = Grammar(TestParserMisc.essay_grammar())
        model = 'microsoft/Phi-3-mini-128k-instruct'
        tokenizer = common.load_tokenizer(model)
        inc_parser = create_parser(grammar)
        r = inc_parser.get_acceptable_next_terminals("I")
        dfa_mask = DFAMaskStore.load_dfa_mask_store(grammar=grammar, tokenizer=tokenizer, use_cache=False, logger=common.EmptyLogger())
        mask = dfa_mask.get_accept_mask(r, get_list=True)
        self.assertIn(' have', mask)
    
    def test_mask_store_misc3(self):
        grammar = Grammar(TestParserMisc.essay_grammar())
        model = 'microsoft/Phi-3-mini-128k-instruct'
        tokenizer = common.load_tokenizer(model)
        inc_parser = create_parser(grammar)
        r = inc_parser.get_acceptable_next_terminals("I have been working there for 5 years.")
        dfa_mask = DFAMaskStore.load_dfa_mask_store(grammar=grammar, tokenizer=tokenizer, use_cache=False, logger=common.EmptyLogger())
        mask = dfa_mask.get_accept_mask(r, get_list=True)
        self.assertIn(' I', mask)

    def test_parser_calc(self):
        inc_parser = create_parser(Grammar('calc'))
        partial_code = "113 + 235 + 17"
        r = inc_parser.get_acceptable_next_terminals(partial_code)
        self.assertEqual(r.remainder, '17')
        self.assertIn(AcceptSequence(['NUMBER', 'PLUS']), r.accept_sequences)
        self.assertIn(AcceptSequence(['NUMBER', 'STAR']), r.accept_sequences)
        self.assertIn(AcceptSequence(['LPAR']), r.accept_sequences)

    def test_parser_calc2(self):
        inc_parser = create_parser(Grammar('calc'))
        partial_code = "11333"
        r = inc_parser.get_acceptable_next_terminals(partial_code)
        self.assertEqual(r.remainder, '11333')
        self.assertIn(AcceptSequence(['NUMBER', 'PLUS']), r.accept_sequences)

    def test_parser_prover9(self):
        inc_parser = create_parser(Grammar('prover9'))
        partial_code = f"""Predicates:
Dependent(x) ::: x is a person dependent on caffeine.
Drinks(x) ::: x regularly drinks coffee.
Jokes(x) ::: x jokes about being addicted to caffeine.
Unaware(x) ::: x is unaware that caffeine is a drug.
Student(x) ::: x is a student.
Premises:
∀x (Drinks(x) → Dependent(x)) ::: All people who regularly drink coffee are dependent on caffeine.
∀x (Drinks(x) ⊕ Jokes(x)) ::: People either regularly drink coffee or joke about being addicted to caffeine.
∀x (Jokes(x) → ¬Unaware(x)) ::: No one who jokes about being addicted to caffeine is unaware that caffeine is a drug. 
(Student(rina) ∧ Unaware(rina)) ⊕ ¬(Student(rina) ∨ Unaware(rina)) ::: Rina is either a student and unaware that caffeine is a drug, or neither a student nor unaware that caffeine is a drug. 
¬(Dependent(rina) ∧ Student(rina)) → (Dependent(rina) ∧ Student(rina)) ⊕ ¬(Dependent(rina) ∨ Student(rina)) ::: If Rina is not a person dependent on caffeine and a student, then Rina is either a person dependent on caffeine and a student, or neither a person dependent on caffeine nor a student.
Conclusion:
Jokes(rina) ⊕ Unaware(rina) ::: Rina is either a person who jokes about being addicted to caffeine or is unaware that caffeine is a drug.
((Jokes(rina) ∧ Unaware(rina)) ⊕ ¬(Jokes(rina) ∨ Unaware(rina))) → (Jokes(rina) ∧ Drinks(rina)) ::: If Rina is either a person who jokes about being addicted to caffeine and a person who is unaware that caffeine is a drug, or neither a person who jokes about being addicted to caffeine nor a person who is unaware that caffeine is a drug, then Rina jokes about being addicted to caffeine and regularly drinks coffee.
        """
        r = inc_parser.base_parser.parse(partial_code)
        # print(r.pretty())

    def test_parser_prover9_2(self):
        inc_parser = create_parser(Grammar('prover9'))
        partial_code = f"""Predicates:\nPer"""
        r = inc_parser.get_acceptable_next_terminals(partial_code)
        print(r)
