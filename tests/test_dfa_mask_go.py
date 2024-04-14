import sys
import os
import time
import unittest
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
import syncode.common as common
from syncode.parsers.incremental_parser import ParseResult
from syncode.parse_result import AcceptSequence, RemainderState
from syncode.dfa_mask_store import DFAMaskStore
from syncode.parsers.grammars.grammar import Grammar

# Initialize these outside the test class if they're shared across tests
model = 'deepseek-ai/deepseek-coder-6.7b-instruct'
# model = 'Llama-7b'
tokenizer = common.load_tokenizer(model)
dfa_mask = DFAMaskStore.load_dfa_mask_store(grammar=Grammar('go'), tokenizer=tokenizer, use_cache=True, logger=common.EmptyLogger())

class TestDFAMask(unittest.TestCase):
    def test_dfa_mask(self):
        query_start_time = time.time()
        r = ParseResult({AcceptSequence(['DECIMAL_LIT', 'PLUS'])}, '1', RemainderState.MAYBE_COMPLETE)
        dfa_mask.get_accept_mask(r)  # This is just to run the function, assuming you're checking time
        # self.assertLess(time.time() - query_start_time, 0.02, "Mask query took too long")

        query_start_time = time.time()
        r = ParseResult({AcceptSequence(['DECIMAL_LIT', 'PLUS'])}, '1', RemainderState.MAYBE_COMPLETE)
        dfa_mask.get_accept_mask(r, get_list=True)
        # self.assertLess(time.time() - query_start_time, 10**-4, "List query took too long")
        result_list = dfa_mask.get_accept_mask(r, get_list=True)
        for token in [' +', ' +=', ' ++']:
            self.assertIn(token, result_list, f"{token} not found in result list")

    def test_dfa_mask2(self):
        r = ParseResult({AcceptSequence(['EOS'])}, '\n // 1.', RemainderState.MAYBE_COMPLETE)
        result_list = dfa_mask.get_accept_mask(r, get_list=True)
        self.assertTrue(len(result_list) > 32000, "Result list is smaller than expected")

    def test_dfa_mask3(self):
        r = ParseResult({AcceptSequence(['__ANON_14'])}, '', RemainderState.COMPLETE)
        result_list = dfa_mask.get_accept_mask(r, get_list=True)
        # Uncomment the following line if you want to assert presence of specific tokens
        # self.assertIn(":=", result_list, ":= not found in result list")

    def test_dfa_mask4(self):
        r = ParseResult({AcceptSequence(['__IGNORE_0'])}, '', RemainderState.COMPLETE)
        self.assertIn("\t", dfa_mask.get_accept_mask(r, get_list=True), "Tab character not found in result list")

    def test_dfa_mask5(self):
        r = ParseResult({AcceptSequence(['LBRACE', '__IGNORE_0'])}, '{', RemainderState.MAYBE_COMPLETE)
        self.assertIn("\t", dfa_mask.get_accept_mask(r, get_list=True), "Tab character not found in result list")

    def test_dfa_mask6(self):
        r = ParseResult({AcceptSequence(['NAME'])}, 'for', RemainderState.MAYBE_COMPLETE)
        self.assertIn(" {", dfa_mask.get_accept_mask(r, get_list=True), "Opening brace not found in result list")

