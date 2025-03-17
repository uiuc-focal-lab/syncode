import unittest
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../..')
import time
from tests.test_utils import CustomAssertMixin
import syncode.common as common
from syncode.parsers.incremental_parser import ParseResult
from syncode.parse_result import AcceptSequence, IndentationConstraint, RemainderState
from syncode.mask_store.mask_store import MaskStore
from syncode.parsers import create_parser
from syncode.parsers.grammars.grammar import Grammar
import logging
logger = logging.getLogger(__name__)


class TestDFAMaskLlama(unittest.TestCase, CustomAssertMixin):
    model = 'meta-llama/Llama-2-7b-hf'
    tokenizer = common.load_tokenizer(model)
    mask_store = MaskStore.init_mask_store(
        grammar=Grammar('python'), 
        tokenizer=tokenizer, 
        use_cache=True, 
        indent=True, 
        mode="grammar_strict"
        )

    @classmethod
    def setUpClass(cls):
        """Configure logging before any tests run."""
        super().setUpClass()
        common.setup_logging()

    def test_strict(self):        
        query_start_time = time.time()
        r = ParseResult({AcceptSequence(['DEC_NUMBER', 'PLUS'])}, b'1', RemainderState.MAYBE_COMPLETE)
        self.mask_store.get_accept_mask(r)  # Assuming dfa_mask is accessible
        time_taken_for_mask_query = time.time() - query_start_time

        query_start_time = time.time()
        r = ParseResult({AcceptSequence(['DEC_NUMBER', 'PLUS'])}, b'1', RemainderState.MAYBE_COMPLETE)
        self.mask_store.get_accept_mask(r, get_list=True)
        time_taken_for_list_query = time.time() - query_start_time
        logger.info(f"Time taken for mask query: {time_taken_for_mask_query} and list query: {time_taken_for_list_query}")

        ac_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertInWithLimit(' +', ac_list)
        self.assertNotIn(' +=', ac_list) # In strict mode this should not be present
        self.assertNotIn(' ++', ac_list) # In strict mode this should not be present


    def test_dfa_mask2(self):
        r = ParseResult({AcceptSequence(['NAME'])}, b'\n"""comment"""\n', RemainderState.MAYBE_COMPLETE)
        ac_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertGreaterWithLimit(len(ac_list), 0, ac_list)

    def test_dfa_mask3(self):
        r = ParseResult({AcceptSequence(['STRING', 'FOR'])}, b'"Return only negative numbers in the list.  Note that this is not the same as the negative of the list. ', RemainderState.MAYBE_COMPLETE)
        ac_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertGreaterWithLimit(len(ac_list), 0, ac_list)

    def test_dfa_mask4(self):
        r = ParseResult({AcceptSequence(['NAME', 'LPAR'])}, b'upper', RemainderState.MAYBE_COMPLETE)
        ac_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertInWithLimit('(', ac_list)

    def test_dfa_mask5(self):
        s = b'\n\t""" Check if in given list of numbers, are any two numbers closer to each other than\n\tgiven threshold.\n\t>>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n\tFalse\n\t>>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n\tTrue\n\t"""\n'
        r = ParseResult({AcceptSequence(['_NL', 'NAME'])}, s, RemainderState.MAYBE_COMPLETE)
        ac_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertTrueWithLimit(all([t in ac_list for t in ['\t', '\n', '""', '#', "''", "'", '"']]), ['\t', '\n', '""', '#', "''", "'", '"'], ac_list)

    def test_dfa_mask6(self):
        r = ParseResult({AcceptSequence(['DEC_NUMBER', 'COLON'])}, b'2', RemainderState.MAYBE_COMPLETE)
        ac_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertFalse(any([t in ac_list for t in ['+', '#', '-', '*']]))

    def test_dfa_mask7(self):
        r = ParseResult({AcceptSequence(['LPAR'])}, b'', RemainderState.COMPLETE)
        ac_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertEqual(len([ac for ac in ac_list if 'num' in ac]), 0)
        self.assertGreater(len([ac for ac in ac_list if '(' in ac]), 0)

    def test_dfa_mask8(self):
        r = ParseResult({AcceptSequence(['NAME', 'LPAR'])}, b'print', RemainderState.MAYBE_COMPLETE)
        ac_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertNotIn(' num', ac_list)
        self.assertInWithLimit('num', ac_list)
        self.assertInWithLimit('(', ac_list)

    def test_special_token(self):
        r = ParseResult({AcceptSequence(['_NL'])}, b'', RemainderState.COMPLETE)
        ac_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertInWithLimit('<s>', ac_list)  # special token should always be in the list

    def test_eos_token(self):
        # EOS token should be in the list if $END is in the accept sequence
        r = ParseResult({AcceptSequence(['$END'])}, b'', RemainderState.COMPLETE)
        ac_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertInWithLimit('</s>', ac_list)

        # EOS token should be in the list if $END is in the accept sequence
        r = ParseResult({AcceptSequence(['RPAR', '$END'])}, b')', RemainderState.MAYBE_COMPLETE)
        ac_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertInWithLimit('</s>', ac_list)

        # EOS token should not be in the list if $END is not in the accept sequence
        r = ParseResult({AcceptSequence(['NAME'])}, b'', RemainderState.COMPLETE)
        ac_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertNotIn('</s>', ac_list)

    def test_dfa_mask13(self):
        r = ParseResult({AcceptSequence(['NAME']), AcceptSequence(['RETURN', 'NAME'])}, b'return', RemainderState.MAYBE_COMPLETE, next_ac_indents=None)
        ac_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertInWithLimit("ing", ac_list)
        self.assertInWithLimit(" x", ac_list)

    def test_indent(self):
        ac_list = self.mask_store._lookup_table.get_indentation_tokens(IndentationConstraint(accept_indents=[1]), get_list=True)
        self.assertTrue(all(t in ac_list for t in [' int', ' ']))
        self.assertFalse('  ' in ac_list)

        ac_list = self.mask_store._lookup_table.get_indentation_tokens(IndentationConstraint(accept_indents=[2]), get_list=True)
        self.assertTrue(all(t in ac_list for t in [' ', '  ']))

        ac_list = self.mask_store._lookup_table.get_indentation_tokens(IndentationConstraint(accept_indents=[4]), get_list=True)
        self.assertTrue(all(t in ac_list for t in ['\t', ' ', '  ', '    ', '   ', ' ']))

        ac_list = self.mask_store._lookup_table.get_indentation_tokens(IndentationConstraint(greater_than_indent_val=0), get_list=True)
        self.assertInWithLimit(' int', ac_list)

        ac_list = self.mask_store._lookup_table.get_indentation_tokens(IndentationConstraint(greater_than_indent_val=1), get_list=True)
        self.assertFalse(' int' in ac_list)
        self.assertTrue('  ' in ac_list)

        ac_list = self.mask_store._lookup_table.get_indentation_tokens(IndentationConstraint(greater_than_indent_val=3), get_list=True)
        self.assertIn('              ', ac_list)

    def test_dfa_mask_with_indent(self):
        r = ParseResult({AcceptSequence(['NAME'])}, b'int', RemainderState.COMPLETE, IndentationConstraint(accept_indents=[0]))
        ac_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertInWithLimit('int', ac_list)

        r = ParseResult({AcceptSequence(['IF'])}, b'', RemainderState.COMPLETE, IndentationConstraint(accept_indents=[1]))
        ac_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertInWithLimit(' if', ac_list)

        r = ParseResult({AcceptSequence(['NAME'])}, b'int', RemainderState.COMPLETE, IndentationConstraint(greater_than_indent_val=0))
        ac_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertInWithLimit(' int', ac_list)

        r = ParseResult({AcceptSequence(['NAME'])}, b'', RemainderState.COMPLETE, IndentationConstraint(greater_than_indent_val=1))
        ac_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertNotIn(' int', ac_list)

        r = ParseResult({AcceptSequence(['IF'])}, b'', RemainderState.COMPLETE, IndentationConstraint(accept_indents=[0]))
        ac_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertInWithLimit('if', ac_list)
        
        r = ParseResult({AcceptSequence(['_NL', 'RETURN'])}, b'\n\t\t', RemainderState.MAYBE_COMPLETE, IndentationConstraint(greater_than_indent_val=-1))
        ac_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertInWithLimit('return', ac_list)


    @unittest.skip("Skipping the correctness comparison test.")
    def test_indentation(self):
        from mxeval.data import get_data
        mbpp = get_data("mbxp", "python")
        p = create_parser('python')
        self.assertEqual(p._get_indentation(mbpp['MBPP/1']["prompt"]), 4)
        self.assertEqual(p._get_indentation(mbpp['MBPP/2']["prompt"]), 2)
        self.assertEqual(p._get_indentation(mbpp['MBPP/8']["prompt"]), 1)


    @unittest.skip("Skipping the correctness comparison test.")
    def test_simplifications(self):
        import regex
        simplifications = Grammar('python').simplifications()
        
        # COMMENT 
        reg = simplifications['COMMENT']
        self.assertIsNotNone(regex.match(reg, '# Hello'))
        self.assertIsNotNone(regex.match(reg, '""" Foo \n Bar """'))
        self.assertIsNotNone(regex.match(reg, "''' Foo \n Bar '''"))

        # LONG_STRING
        reg = simplifications['LONG_STRING']
        self.assertIsNotNone(regex.match(reg, '""" Foo \n Bar """'))
        self.assertIsNotNone(regex.match(reg, "''' Foo \n Bar '''"))
        self.assertIsNone(regex.match(reg, '""" Foo \n Bar '))
        self.assertIsNone(regex.match(reg, "''' Foo \n Bar "))

        # STRING
        reg = simplifications['STRING']
        self.assertIsNotNone(regex.match(reg, '"Foo"'))
        self.assertIsNotNone(regex.match(reg, "'Foo'"))
        self.assertIsNone(regex.match(reg, '"Foo'))
        self.assertIsNone(regex.match(reg, "'Foo"))

        # _NL
        reg = simplifications['_NL']
        self.assertIsNotNone(regex.match(reg, '\n'))
        self.assertIsNotNone(regex.match(reg, '\n\n'))
        self.assertIsNotNone(regex.match(reg, '\n""" Foo \n Bar """'))
        self.assertIsNotNone(regex.match(reg, '\n# Hello!'))


class TestDFAMaskCodegen(unittest.TestCase, CustomAssertMixin):
    model = 'Salesforce/codegen-350M-multi'
    tokenizer = common.load_tokenizer(model)
    mask_store = MaskStore.init_mask_store(
        grammar=Grammar('python'), 
        tokenizer=tokenizer, 
        use_cache=True, 
        indent=True, 
        mode="grammar_mask"
        )

    def test_overapprox(self):        
        r = ParseResult({AcceptSequence(['DEC_NUMBER', 'PLUS'])}, b'1', RemainderState.MAYBE_COMPLETE)
        self.mask_store.get_accept_mask(r, get_list=True)
        ac_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertInWithLimit(' +', ac_list)
        self.assertInWithLimit(' +=', ac_list) # In overapprox mode this should be present
        self.assertInWithLimit(' ++', ac_list) # In overapprox mode this should be present

    def test_dfa_mask10(self):
        ac_list = self.mask_store.get_accept_mask(ParseResult({AcceptSequence(['STRING'])}, b"'", RemainderState.INCOMPLETE, next_ac_indents=None), get_list=True)
        self.assertInWithLimit(" '.", ac_list)

    def test_dfa_mask11(self):
        ac_list = self.mask_store.get_accept_mask(ParseResult({AcceptSequence(['STRING'])}, b"'", RemainderState.INCOMPLETE, next_ac_indents=None), get_list=True)
        self.assertInWithLimit(" '.", ac_list)

    def test_dfa_mask12(self):
        r = ParseResult({AcceptSequence(['_NL', 'IF'])}, b'\n\t\t', RemainderState.MAYBE_COMPLETE, next_ac_indents=None)
        ac_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertInWithLimit("if", ac_list)

    def test_dfa_mask13(self):
        r = ParseResult({AcceptSequence(['NAME', 'LPAR'])}, b'print', RemainderState.MAYBE_COMPLETE)
        ac_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertNotIn(' num', ac_list)
        self.assertInWithLimit('num', ac_list)
        self.assertInWithLimit('()', ac_list)
    
    def test_dfa_mask14(self):
        r = ParseResult({AcceptSequence(['NAME', 'LPAR'])}, b'upper', RemainderState.MAYBE_COMPLETE)
        ac_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertTrueWithLimit(all([t in ac_list for t in ['()', '(']]), ['()', '('], ac_list)

if __name__ == '__main__':
    run_codegen, run_llama = True, True

    if run_llama:
        suite = unittest.TestLoader().loadTestsFromTestCase(TestDFAMaskLlama)
        unittest.TextTestRunner().run(suite)

    if run_codegen:
        suite = unittest.TestLoader().loadTestsFromTestCase(TestDFAMaskCodegen)
        unittest.TextTestRunner().run(suite)
