import re
import time
import common

nfa = common.load_nfa(use_cache=True)

def test_nfa():        
    query_start_time = time.time()
    nfa.get_overapprox_tokens_mask('1', ['PLUS']) # 0.02 seconds for mask
    print(f'Time taken for mask query:', time.time() - query_start_time, flush=True)

    query_start_time = time.time()
    nfa.get_overapprox_tokens_mask('1', ['PLUS'], get_list=True) # 10^-4 seconds for list
    print(f'Time taken for list query:', time.time() - query_start_time, flush=True)

    assert all(t in nfa.get_overapprox_tokens_mask('1', ['PLUS'], get_list=True) for t in [' +', ' +=', ' ++'])

def test_nfa2():
    assert len(nfa.get_overapprox_tokens_mask('\n"""comment"""\n', ['NAME'], get_list=True)) > 0

def test_nfa3():
    s = '"Return only negative numbers in the list.  Note that this is not the same as the negative of the list. '
    dfa = nfa._terminals_to_dfa['STRING']
    print(dfa)
    print(len(nfa.get_overapprox_tokens_mask(s, ['FOR'], get_list=True)))

def test_nfa4():
    s = 'upper'
    ac_list = nfa.get_overapprox_tokens_mask(s, ['LPAR'], get_list=True)
    assert all([t in ac_list for t in ['()', '(']])

def test_nfa5():
    s = '\n\t""" Check if in given list of numbers, are any two numbers closer to each other than\n\tgiven threshold.\n\t>>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n\tFalse\n\t>>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n\tTrue\n\t"""\n'
    ac_list = nfa.get_overapprox_tokens_mask(s, {'_TAB', 'COMMENT', '_NL'}, get_list=True)
    # This should have \t, \n, and '""' in it
    assert all([t in ac_list for t in ['\t', '\n', '""', '#', "''", "'", '"']])
    
tests = [test_nfa, test_nfa2, test_nfa3, test_nfa4, test_nfa5]
common.run_tests(tests)