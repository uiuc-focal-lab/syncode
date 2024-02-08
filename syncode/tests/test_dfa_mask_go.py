import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
import time
import common
from parsers.incremental_parser import ParseResult
from parse_result import RemainderState
from dfa_mask_store import DFAMaskStore

model = 'Salesforce/codegen-350M-multi'
# model = 'WizardLM/WizardCoder-1B-V1.0'
# model = 'Llama-7b'
tokenizer = common.load_tokenizer(model)
dfa_mask = DFAMaskStore.load_dfa_mask_store(grammar='go', tokenizer=tokenizer, use_cache=True, logger=common.EmptyLogger())

def test_dfa_mask():
    query_start_time = time.time()
    r = ParseResult({}, {'PLUS'}, '1', RemainderState.MAYBE_COMPLETE)
    dfa_mask.get_overapprox_tokens_mask(r) # 0.02 seconds for mask
    print(f'Time taken for mask query:', time.time() - query_start_time, flush=True)

    query_start_time = time.time()
    r = ParseResult({}, {'PLUS'}, '1', RemainderState.MAYBE_COMPLETE)
    dfa_mask.get_overapprox_tokens_mask(r, get_list=True) # 10^-4 seconds for list
    print(f'Time taken for list query:', time.time() - query_start_time, flush=True)
    print(dfa_mask.get_overapprox_tokens_mask(r, get_list=True))
    assert all(t in dfa_mask.get_overapprox_tokens_mask(r, get_list=True) for t in [' +', ' +=', ' ++'])

def test_dfa_mask2():
    r = ParseResult({}, {'EOS'}, '\n // 1.', RemainderState.MAYBE_COMPLETE)
    assert len(dfa_mask.get_overapprox_tokens_mask(r, get_list=True)) == 32000

def test_dfa_mask3():
    r = ParseResult({}, {'__ANON_14', 'EQUAL'}, '', RemainderState.COMPLETE)
    print(dfa_mask.get_overapprox_tokens_mask(r, get_list=True))
    assert ":=" in dfa_mask.get_overapprox_tokens_mask(r, get_list=True)

def test_dfa_mask4():
    r = ParseResult({}, {'__IGNORE_0'}, '', RemainderState.COMPLETE)
    print(dfa_mask.get_overapprox_tokens_mask(r, get_list=True))
    assert "\t" in dfa_mask.get_overapprox_tokens_mask(r, get_list=True)

def test_dfa_mask5():
    r = ParseResult({}, { '__IGNORE_0'}, '==', RemainderState.MAYBE_COMPLETE)
    l = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    print([t for t in l if t.startswith("'") or t.startswith(" '") or t.startswith("  '")])
    assert " '" not in dfa_mask.get_overapprox_tokens_mask(r, get_list=True)

tests = [test_dfa_mask, test_dfa_mask2, test_dfa_mask3, test_dfa_mask4, test_dfa_mask5]
# tests = [test_dfa_mask5]
common.run_tests(tests)
