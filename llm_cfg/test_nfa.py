import re
import time
import common
from incremental_parser import IncrementalParser, ParseResult
from parse_result import RemainderState

nfa = common.load_nfa(use_cache=True)

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
    r = ParseResult({}, {'NAME'}, '\n"""comment"""\n', RemainderState.MAYBE_COMPLETE)
    assert len(nfa.get_overapprox_tokens_mask(r, get_list=True)) > 0

def test_nfa3():
    r = ParseResult({'FOR'}, None, '"Return only negative numbers in the list.  Note that this is not the same as the negative of the list. ', False)
    print(len(nfa.get_overapprox_tokens_mask(r, get_list=True)))

def test_nfa4():
    r = ParseResult({}, {'LPAR'}, 'upper', RemainderState.MAYBE_COMPLETE)
    ac_list = nfa.get_overapprox_tokens_mask(r, get_list=True)
    assert all([t in ac_list for t in ['()', '(']])

def test_nfa5():
    s = '\n\t""" Check if in given list of numbers, are any two numbers closer to each other than\n\tgiven threshold.\n\t>>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n\tFalse\n\t>>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n\tTrue\n\t"""\n'
    r = ParseResult({}, {'NAME'}, s, RemainderState.MAYBE_COMPLETE)
    ac_list = nfa.get_overapprox_tokens_mask(r, get_list=True)
    # This should have \t, \n, and '""' in it
    assert all([t in ac_list for t in ['\t', '\n', '""', '#', "''", "'", '"']])

def test_nfa6():
    # negative test
    r = ParseResult({}, {'COLON'}, '2', RemainderState.MAYBE_COMPLETE)
    ac_list = nfa.get_overapprox_tokens_mask(r, get_list=True)
    assert not any([t in ac_list for t in ['+', '#', '-', '*']])

def test_nfa7():
    # negative test
    r = ParseResult({}, {'LPAR'}, '', RemainderState.COMPLETE)
    ac_list = nfa.get_overapprox_tokens_mask(r, get_list=True)
    assert len([ac for ac in ac_list if 'num' in ac]) == 0
    assert len([ac for ac in ac_list if '(' in ac]) > 0

def test_nfa8():
    # negative test
    r = ParseResult({'NAME'}, {'LPAR'}, 'print', RemainderState.MAYBE_COMPLETE)
    ac_list = nfa.get_overapprox_tokens_mask(r, get_list=True)
    assert ' num' not in ac_list
    assert 'num' in ac_list
    assert '()' in ac_list

def test_indetantaion():
    from mxeval.data import get_data
    mbpp = get_data("mbxp", "python")
    p = IncrementalParser()
    assert p._get_indentation(mbpp['MBPP/1']["prompt"]) == 4
    assert p._get_indentation(mbpp['MBPP/2']["prompt"]) == 2
    assert p._get_indentation(mbpp['MBPP/8']["prompt"]) == 1

tests = [test_nfa, test_nfa2, test_nfa3, test_nfa4, test_nfa5, test_nfa6, test_nfa7, test_nfa8, test_indetantaion]
common.run_tests(tests)
