import sys
import os
import time
import unittest
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../..')
import syncode.common as common
from syncode.parsers.incremental_parser import ParseResult
from syncode.parse_result import AcceptSequence, RemainderState
from syncode.mask_store.mask_store import MaskStore
from syncode.parsers.grammars.grammar import Grammar
from tests.test_utils import CustomAssertMixin


# Initialize these outside the test class if they're shared across tests
model = 'Qwen/Qwen2.5-1.5B-Instruct'
tokenizer = common.load_tokenizer(model)
mask_store = MaskStore.init_mask_store(grammar=Grammar('go'), tokenizer=tokenizer, use_cache=True, mode='grammar_mask')

class TestDFAMask(unittest.TestCase, CustomAssertMixin):
    def test_dfa_mask(self):
        r = ParseResult({AcceptSequence(['DECIMAL_LIT', 'PLUS'])}, b'1', RemainderState.MAYBE_COMPLETE)
        mask_store.get_accept_mask(r, get_list=True)
        result_list = mask_store.get_accept_mask(r, get_list=True)
        for token in [' +', ' +=', ' ++']:
            self.assertInWithLimit(token, result_list, f"{token} not found in result list")

    def test_dfa_mask2(self):
        r = ParseResult({AcceptSequence(['EOS'])}, b'\n // 1.', RemainderState.MAYBE_COMPLETE)
        result_list = mask_store.get_accept_mask(r, get_list=True)
        self.assertTrue(len(result_list) > 32000, "Result list is smaller than expected")

    def test_dfa_mask3(self):
        r = ParseResult({AcceptSequence(['__ANON_14'])}, b'', RemainderState.COMPLETE)
        result_list = mask_store.get_accept_mask(r, get_list=True)
        # Uncomment the following line if you want to assert presence of specific tokens
        self.assertInWithLimit(":=", result_list, ":= not found in result list")

    def test_dfa_mask4(self):
        r = ParseResult({AcceptSequence(['__IGNORE_0'])}, b'', RemainderState.COMPLETE)
        self.assertInWithLimit("\t", mask_store.get_accept_mask(r, get_list=True), "Tab character not found in result list")

    def test_dfa_mask5(self):
        r = ParseResult({AcceptSequence(['LBRACE', '__IGNORE_0'])}, b'{', RemainderState.MAYBE_COMPLETE)
        self.assertInWithLimit("\t", mask_store.get_accept_mask(r, get_list=True), "Tab character not found in result list")

    def test_dfa_mask6(self):
        r = ParseResult({AcceptSequence(['NAME'])}, b'for', RemainderState.MAYBE_COMPLETE)
        self.assertInWithLimit(" {", mask_store.get_accept_mask(r, get_list=True), "Opening brace not found in result list")
