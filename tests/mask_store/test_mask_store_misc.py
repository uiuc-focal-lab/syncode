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


class TestMaskGo(unittest.TestCase, CustomAssertMixin):
    def setUp(self):
        model = 'Qwen/Qwen2.5-1.5B-Instruct'
        tokenizer = common.load_tokenizer(model)
        self.mask_store = MaskStore.init_mask_store(grammar=Grammar('go'), tokenizer=tokenizer, use_cache=False, mode='grammar_mask')
        return super().setUp()

    def test_mask(self):
        r = ParseResult({AcceptSequence(['DECIMAL_LIT', 'PLUS'])}, b'1', RemainderState.MAYBE_COMPLETE)
        self.mask_store.get_accept_mask(r, get_list=True)
        result_list = self.mask_store.get_accept_mask(r, get_list=True)
        for token in [' +', ' +=', ' ++']:
            self.assertInWithLimit(token, result_list, f"{token} not found in result list")

    def test_mask2(self):
        r = ParseResult({AcceptSequence(['EOS'])}, b'\n // 1.', RemainderState.MAYBE_COMPLETE)
        result_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertTrue(len(result_list) > 32000, "Result list is smaller than expected")

    def test_mask3(self):
        r = ParseResult({AcceptSequence(['__ANON_14'])}, b'', RemainderState.COMPLETE)
        result_list = self.mask_store.get_accept_mask(r, get_list=True)
        # Uncomment the following line if you want to assert presence of specific tokens
        self.assertInWithLimit(":=", result_list, ":= not found in result list")

    def test_mask4(self):
        r = ParseResult({AcceptSequence(['__IGNORE_0'])}, b'', RemainderState.COMPLETE)
        self.assertInWithLimit("\t", self.mask_store.get_accept_mask(r, get_list=True), "Tab character not found in result list")

    def test_mask5(self):
        r = ParseResult({AcceptSequence(['LBRACE', '__IGNORE_0'])}, b'{', RemainderState.MAYBE_COMPLETE)
        self.assertInWithLimit("\t", self.mask_store.get_accept_mask(r, get_list=True), "Tab character not found in result list")

    def test_mask6(self):
        r = ParseResult({AcceptSequence(['NAME'])}, b'for', RemainderState.MAYBE_COMPLETE)
        self.assertInWithLimit(" {", self.mask_store.get_accept_mask(r, get_list=True), "Opening brace not found in result list")


class TestMaskJSON(unittest.TestCase, CustomAssertMixin):
    def setUp(self):
        model = 'google/gemma-2-2b-it'
        tokenizer = common.load_tokenizer(model)

        custom_json_grammar = f"""
        ?start: start_value
        ?start_value: object
        | array

        ?value: object
        | array
        | EMPTY_STRING
        | NONEMPTY_STRING
        | SIGNED_NUMBER      -> number
        | "true"             -> true
        | "false"            -> false
        | "null"             -> null

        array  : "[" [value ("," value)*] "]"
        object : "{" [pair ("," pair)*] "}"
        pair   : NONEMPTY_STRING ":" value

        NONEMPTY_STRING: /\"[^"”“]+\"/
        EMPTY_STRING: /\"\"/

        DIGIT: "0".."9"
        HEXDIGIT: "a".."f"|"A".."F"|DIGIT
        INT: DIGIT+
        SIGNED_INT: ["+"|"-"] INT
        DECIMAL: INT "." INT? | "." INT


        _EXP: ("e"|"E") SIGNED_INT
        FLOAT: INT _EXP | DECIMAL _EXP?
        NUMBER: FLOAT | INT
        SIGNED_NUMBER: ["+"|"-"] NUMBER
        WS: /[ \t\f\r\n]/+

        %ignore WS
        """
        self.mask_store = MaskStore.init_mask_store(grammar=Grammar(custom_json_grammar), tokenizer=tokenizer, use_cache=False, mode='grammar_mask')
        return super().setUp()
    
    def test_mask(self):
        r = ParseResult({AcceptSequence(['NONEMPTY_STRING'])}, b'"key', RemainderState.INCOMPLETE)
        result_list = self.mask_store.get_accept_mask(r, get_list=True)
        self.assertInWithLimit('"', result_list, '" not found in result list')
        self.assertNotIn('”', result_list)
        self.assertNotIn('“', result_list)        


if __name__ == '__main__':
    # Run JSON tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMaskJSON)
    unittest.TextTestRunner().run(suite)