import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
import time
import common
from parsers.incremental_parser import ParseResult
from parse_result import AcceptSequence, RemainderState
from dfa_mask_store import DFAMaskStore

# model = 'Salesforce/codegen-350M-multi'
# model = 'WizardLM/WizardCoder-1B-V1.0'
model = 'Llama-7b'
model = 'deepseek-ai/deepseek-coder-6.7b-instruct'
tokenizer = common.load_tokenizer(model)
dfa_mask = DFAMaskStore.load_dfa_mask_store(grammar='go', tokenizer=tokenizer, use_cache=True, logger=common.EmptyLogger())

def test_dfa_mask():
    query_start_time = time.time()
    r = ParseResult({AcceptSequence(['DECIMAL_LIT', 'PLUS'])}, '1', RemainderState.MAYBE_COMPLETE)
    dfa_mask.get_overapprox_tokens_mask(r) # 0.02 seconds for mask
    print(f'Time taken for mask query:', time.time() - query_start_time, flush=True)

    query_start_time = time.time()
    r = ParseResult({AcceptSequence(['DECIMAL_LIT', 'PLUS'])}, '1', RemainderState.MAYBE_COMPLETE)
    dfa_mask.get_overapprox_tokens_mask(r, get_list=True) # 10^-4 seconds for list
    print(f'Time taken for list query:', time.time() - query_start_time, flush=True)
    print(dfa_mask.get_overapprox_tokens_mask(r, get_list=True))
    assert all(t in dfa_mask.get_overapprox_tokens_mask(r, get_list=True) for t in [' +', ' +=', ' ++'])

def test_dfa_mask2():
    r = ParseResult({AcceptSequence(['EOS'])}, '\n // 1.', RemainderState.MAYBE_COMPLETE)
    print(len(dfa_mask.get_overapprox_tokens_mask(r, get_list=True)))
    assert len(dfa_mask.get_overapprox_tokens_mask(r, get_list=True)) > 32000

# TODO: Fix
def test_dfa_mask3():
    r = ParseResult({AcceptSequence(['__ANON_14'])}, '', RemainderState.COMPLETE)
    print(dfa_mask.get_overapprox_tokens_mask(r, get_list=True))
    # assert ":=" in dfa_mask.get_overapprox_tokens_mask(r, get_list=True)

def test_dfa_mask4():
    r = ParseResult({AcceptSequence(['__IGNORE_0'])}, '', RemainderState.COMPLETE)
    assert "\t" in dfa_mask.get_overapprox_tokens_mask(r, get_list=True)

def test_dfa_mask5():
    r = ParseResult({AcceptSequence(['LBRACE', '__IGNORE_0'])}, '{', RemainderState.MAYBE_COMPLETE)
    assert "\t" in dfa_mask.get_overapprox_tokens_mask(r, get_list=True)

def test_dfa_mask6():
    # TODO: imprecision
    r = ParseResult({AcceptSequence(['NAME'])}, 'for', RemainderState.MAYBE_COMPLETE)
    assert " {" in dfa_mask.get_overapprox_tokens_mask(r, get_list=True)


tests = [test_dfa_mask, test_dfa_mask2, test_dfa_mask3, test_dfa_mask4, test_dfa_mask5, test_dfa_mask6] 
common.run_tests(tests)
