import sys, os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
import time
import common
from incremental_parser import ParseResult
from grammars.python_parser import PythonIncrementalParser
from parse_result import IndentationConstraint, RemainderState
from transformers import AutoTokenizer
from dfa_mask_store import load_dfa_mask_store

tokenizer = AutoTokenizer.from_pretrained(common.HF_CACHE+'Llama-7b', cache_dir=common.HF_CACHE, token=common.HF_ACCESS_TOKEN, trust_remote_code=True)
dfa_mask = load_dfa_mask_store(grammar='python', tokenizer=tokenizer, use_cache=True, logger=common.TestLogger())

def test_dfa_mask():        
    query_start_time = time.time()
    r = ParseResult({}, {'PLUS'}, '1', RemainderState.MAYBE_COMPLETE)
    dfa_mask.get_overapprox_tokens_mask(r) # 0.02 seconds for mask
    print(f'Time taken for mask query:', time.time() - query_start_time, flush=True)

    query_start_time = time.time()
    r = ParseResult({}, {'PLUS'}, '1', RemainderState.MAYBE_COMPLETE)
    dfa_mask.get_overapprox_tokens_mask(r, get_list=True) # 10^-4 seconds for list
    print(f'Time taken for list query:', time.time() - query_start_time, flush=True)

    assert all(t in dfa_mask.get_overapprox_tokens_mask(r, get_list=True) for t in [' +', ' +=', ' ++'])

def test_dfa_mask2():
    r = ParseResult({}, {'NAME'}, '\n"""comment"""\n', RemainderState.MAYBE_COMPLETE)
    assert len(dfa_mask.get_overapprox_tokens_mask(r, get_list=True)) > 0

def test_dfa_mask3():
    r = ParseResult({'FOR'}, None, '"Return only negative numbers in the list.  Note that this is not the same as the negative of the list. ', False)
    print(len(dfa_mask.get_overapprox_tokens_mask(r, get_list=True)))

def test_dfa_mask4():
    r = ParseResult({}, {'LPAR'}, 'upper', RemainderState.MAYBE_COMPLETE)
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    assert all([t in ac_list for t in ['()', '(']])

def test_dfa_mask5():
    s = '\n\t""" Check if in given list of numbers, are any two numbers closer to each other than\n\tgiven threshold.\n\t>>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n\tFalse\n\t>>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n\tTrue\n\t"""\n'
    r = ParseResult({}, {'NAME'}, s, RemainderState.MAYBE_COMPLETE)
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    # This should have \t, \n, and '""' in it
    assert all([t in ac_list for t in ['\t', '\n', '""', '#', "''", "'", '"']])

def test_dfa_mask6():
    # negative test
    r = ParseResult({}, {'COLON'}, '2', RemainderState.MAYBE_COMPLETE)
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    assert not any([t in ac_list for t in ['+', '#', '-', '*']])

def test_dfa_mask7():
    # negative test
    r = ParseResult({}, {'LPAR'}, '', RemainderState.COMPLETE)
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    assert len([ac for ac in ac_list if 'num' in ac]) == 0
    assert len([ac for ac in ac_list if '(' in ac]) > 0

def test_dfa_mask8():
    # negative test
    r = ParseResult({'NAME'}, {'LPAR'}, 'print', RemainderState.MAYBE_COMPLETE)
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    assert ' num' not in ac_list
    assert 'num' in ac_list
    assert '()' in ac_list

def test_dfa_mask9():
    r = ParseResult({}, {}, '', RemainderState.MAYBE_COMPLETE)
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    assert '</s>' in ac_list # special token should always be in the list

def test_indent():
    ac_list = dfa_mask._get_indentation_tokens(IndentationConstraint(accept_indents=[1]), get_list=True)
    assert all(t in ac_list for t in [' int', ' '])
    assert not '  ' in ac_list
    ac_list = dfa_mask._get_indentation_tokens(IndentationConstraint(accept_indents=[2]), get_list=True)
    assert all(t in ac_list for t in [' ', '  '])
    ac_list = dfa_mask._get_indentation_tokens(IndentationConstraint(accept_indents=[4]), get_list=True)
    assert all(t in ac_list for t in ['\t', ' ', '  ', '    ', '   ', ' '])
    ac_list = dfa_mask._get_indentation_tokens(IndentationConstraint(greater_than_indent_val=0), get_list=True)
    assert ' int' in ac_list
    ac_list = dfa_mask._get_indentation_tokens(IndentationConstraint(greater_than_indent_val=1), get_list=True)
    assert not ' int' in ac_list
    assert '  ' in ac_list
    ac_list = dfa_mask._get_indentation_tokens(IndentationConstraint(greater_than_indent_val=3), get_list=True)
    assert '              ' in ac_list

def test_dfa_mask_with_indent():
    r = ParseResult({'NAME'}, {'NAME'}, '', RemainderState.COMPLETE, IndentationConstraint(accept_indents=[0]))
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    assert 'int' in ac_list

    r = ParseResult({}, {'IF'}, '', RemainderState.COMPLETE, IndentationConstraint(accept_indents=[1]))
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    assert ' if' in ac_list

    r = ParseResult({'NAME'}, {'NAME'}, '', RemainderState.COMPLETE, IndentationConstraint(greater_than_indent_val=0))
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    assert ' int' in ac_list

    r = ParseResult({'NAME'}, {'NAME'}, '', RemainderState.COMPLETE, IndentationConstraint(greater_than_indent_val=1))
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    assert not ' int' in ac_list

    r = ParseResult({}, {'IF'}, '', RemainderState.MAYBE_COMPLETE, IndentationConstraint(accept_indents=[0]))
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    assert 'if' in ac_list
    
    r = ParseResult({}, {'RETURN'}, '\n\t\t', RemainderState.MAYBE_COMPLETE, IndentationConstraint(greater_than_indent_val=-1))
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    assert 'return' in ac_list


def test_indetantaion():
    from mxeval.data import get_data
    mbpp = get_data("mbxp", "python")
    p = PythonIncrementalParser()
    assert p._get_indentation(mbpp['MBPP/1']["prompt"]) == 4
    assert p._get_indentation(mbpp['MBPP/2']["prompt"]) == 2
    assert p._get_indentation(mbpp['MBPP/8']["prompt"]) == 1

tests = [test_dfa_mask, test_dfa_mask2, test_dfa_mask3, test_dfa_mask4, test_dfa_mask5, test_dfa_mask6, test_dfa_mask7, test_dfa_mask8, test_dfa_mask9, test_indent, test_dfa_mask_with_indent]
common.run_tests(tests)
