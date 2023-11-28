import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
import time
import common
from incremental_parser import ParseResult
from grammars.python_parser import PythonIncrementalParser
from parse_result import IndentationConstraint, RemainderState

nfa = common.load_nfa(language='go', use_cache=True)

def test_nfa():        
    query_start_time = time.time()
    r = ParseResult({}, {'PLUS'}, '1', RemainderState.MAYBE_COMPLETE)
    nfa.get_overapprox_tokens_mask(r) # 0.02 seconds for mask
    print(f'Time taken for mask query:', time.time() - query_start_time, flush=True)

    query_start_time = time.time()
    r = ParseResult({}, {'PLUS'}, '1', RemainderState.MAYBE_COMPLETE)
    nfa.get_overapprox_tokens_mask(r, get_list=True) # 10^-4 seconds for list
    print(f'Time taken for list query:', time.time() - query_start_time, flush=True)
    assert all(t in nfa.get_overapprox_tokens_mask(r, get_list=True) for t in [' +', ' +=', ' ++'])

def test_nfa2():
    r = ParseResult({}, {'EOS'}, '\n // 1.', RemainderState.MAYBE_COMPLETE)
    assert len(nfa.get_overapprox_tokens_mask(r, get_list=True)) == 32000

def test_nfa3():
    r = ParseResult({}, {'__ANON_14', 'EQUAL'}, '', RemainderState.COMPLETE)
    print(nfa.get_overapprox_tokens_mask(r, get_list=True))
    assert ":=" in nfa.get_overapprox_tokens_mask(r, get_list=True)

def test_nfa4():
    r = ParseResult({}, {'__IGNORE_0'}, '', RemainderState.COMPLETE)
    print(nfa.get_overapprox_tokens_mask(r, get_list=True))
    assert "\t" in nfa.get_overapprox_tokens_mask(r, get_list=True)

tests = [test_nfa, test_nfa2, test_nfa3, test_nfa4]
common.run_tests(tests)
