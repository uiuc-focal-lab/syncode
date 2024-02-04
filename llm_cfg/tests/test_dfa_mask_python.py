import sys, os

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
import time
import common
from incremental_parser import ParseResult
from grammars.python_parser import PythonIncrementalParser
from parse_result import AcceptSequence, IndentationConstraint, RemainderState
from dfa_mask_store import DFAMaskStore

def test_dfa_mask():        
    query_start_time = time.time()
    r = ParseResult({AcceptSequence(['DEC_NUMBER', 'PLUS'])}, '1', RemainderState.MAYBE_COMPLETE)
    dfa_mask.get_overapprox_tokens_mask(r) # 0.02 seconds for mask
    print(f'Time taken for mask query:', time.time() - query_start_time, flush=True)

    query_start_time = time.time()
    r = ParseResult({AcceptSequence(['DEC_NUMBER', 'PLUS'])}, '1', RemainderState.MAYBE_COMPLETE)
    dfa_mask.get_overapprox_tokens_mask(r, get_list=True) # 10^-4 seconds for list
    print(f'Time taken for list query:', time.time() - query_start_time, flush=True)

    assert all(t in dfa_mask.get_overapprox_tokens_mask(r, get_list=True) for t in [' +', ' +=', ' ++'])

def test_dfa_mask2():
    r = ParseResult({AcceptSequence(['NAME'])}, '\n"""comment"""\n', RemainderState.MAYBE_COMPLETE)
    assert len(dfa_mask.get_overapprox_tokens_mask(r, get_list=True)) > 0

def test_dfa_mask3():
    r = ParseResult({AcceptSequence(['STRING', 'FOR'])}, '"Return only negative numbers in the list.  Note that this is not the same as the negative of the list. ', RemainderState.MAYBE_COMPLETE)
    assert len(dfa_mask.get_overapprox_tokens_mask(r, get_list=True)) > 0

def test_dfa_mask4():
    r = ParseResult({AcceptSequence(['NAME', 'LPAR'])}, 'upper', RemainderState.MAYBE_COMPLETE)
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    assert all([t in ac_list for t in ['()', '(']])

def test_dfa_mask5():
    s = '\n\t""" Check if in given list of numbers, are any two numbers closer to each other than\n\tgiven threshold.\n\t>>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n\tFalse\n\t>>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n\tTrue\n\t"""\n'
    r = ParseResult({AcceptSequence(['_NL', 'NAME'])}, s, RemainderState.MAYBE_COMPLETE)
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    # This should have \t, \n, and '""' in it
    assert all([t in ac_list for t in ['\t', '\n', '""', '#', "''", "'", '"']])

def test_dfa_mask6():
    # negative test
    r = ParseResult({AcceptSequence(['DEC_NUMBER', 'COLON'])}, '2', RemainderState.MAYBE_COMPLETE)
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    assert not any([t in ac_list for t in ['+', '#', '-', '*']])

def test_dfa_mask7():
    # negative test
    r = ParseResult({AcceptSequence(['LPAR'])}, '', RemainderState.COMPLETE)
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    assert len([ac for ac in ac_list if 'num' in ac]) == 0
    assert len([ac for ac in ac_list if '(' in ac]) > 0

def test_dfa_mask8():
    # negative test
    r = ParseResult({AcceptSequence(['NAME', 'LPAR'])}, 'print', RemainderState.MAYBE_COMPLETE)
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    assert ' num' not in ac_list
    assert 'num' in ac_list
    assert '()' in ac_list

def test_dfa_mask9():
    r = ParseResult({AcceptSequence(['_NL'])}, '', RemainderState.COMPLETE)
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    assert '</s>' in ac_list # special token should always be in the list

def test_dfa_mask10():
    assert " '." in dfa_mask.get_overapprox_tokens_mask(ParseResult({AcceptSequence(['STRING'])}, "'", RemainderState.INCOMPLETE, next_ac_indents=None), get_list=True)

def test_dfa_mask11():
    assert " '." in dfa_mask.get_overapprox_tokens_mask(ParseResult({AcceptSequence(['STRING'])}, "'", RemainderState.INCOMPLETE, next_ac_indents=None), get_list=True)

def test_dfa_mask12():
    r = ParseResult({AcceptSequence(['_NL', 'IF'])}, '\n\t\t', RemainderState.MAYBE_COMPLETE, next_ac_indents=None)
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    assert "if" in ac_list

def test_dfa_mask13():
    r = ParseResult({AcceptSequence(['NAME']), AcceptSequence(['RETURN', 'NAME'])}, 'return', RemainderState.MAYBE_COMPLETE, next_ac_indents=None)
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    assert "ing" in ac_list
    assert " x" in ac_list

def test_indent():
    ac_list = dfa_mask._lookup_table.get_indentation_tokens(IndentationConstraint(accept_indents=[1]), get_list=True)
    assert all(t in ac_list for t in [' int', ' '])
    assert not '  ' in ac_list
    ac_list = dfa_mask._lookup_table.get_indentation_tokens(IndentationConstraint(accept_indents=[2]), get_list=True)
    assert all(t in ac_list for t in [' ', '  '])
    ac_list = dfa_mask._lookup_table.get_indentation_tokens(IndentationConstraint(accept_indents=[4]), get_list=True)
    assert all(t in ac_list for t in ['\t', ' ', '  ', '    ', '   ', ' '])
    ac_list = dfa_mask._lookup_table.get_indentation_tokens(IndentationConstraint(greater_than_indent_val=0), get_list=True)
    assert ' int' in ac_list
    ac_list = dfa_mask._lookup_table.get_indentation_tokens(IndentationConstraint(greater_than_indent_val=1), get_list=True)
    assert not ' int' in ac_list
    assert '  ' in ac_list
    ac_list = dfa_mask._lookup_table.get_indentation_tokens(IndentationConstraint(greater_than_indent_val=3), get_list=True)
    assert '              ' in ac_list

def test_dfa_mask_with_indent():
    r = ParseResult({AcceptSequence(['NAME'])}, 'int', RemainderState.COMPLETE, IndentationConstraint(accept_indents=[0]))
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    assert 'int' in ac_list

    r = ParseResult({AcceptSequence(['IF'])}, '', RemainderState.COMPLETE, IndentationConstraint(accept_indents=[1]))
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    assert ' if' in ac_list

    # r = ParseResult({'NAME'}, {'NAME'}, '', RemainderState.COMPLETE, IndentationConstraint(greater_than_indent_val=0))
    r = ParseResult({AcceptSequence(['NAME'])}, 'int', RemainderState.COMPLETE, IndentationConstraint(greater_than_indent_val=0))
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    assert ' int' in ac_list

    r = ParseResult({AcceptSequence(['NAME'])}, '', RemainderState.COMPLETE, IndentationConstraint(greater_than_indent_val=1))
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    assert not ' int' in ac_list


    r = ParseResult({AcceptSequence(['IF'])}, '', RemainderState.COMPLETE, IndentationConstraint(accept_indents=[0]))
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    assert 'if' in ac_list
    
    r = ParseResult({AcceptSequence(['_NL', 'RETURN'])}, '\n\t\t', RemainderState.MAYBE_COMPLETE, IndentationConstraint(greater_than_indent_val=-1))
    ac_list = dfa_mask.get_overapprox_tokens_mask(r, get_list=True)
    assert 'return' in ac_list


def test_indetantaion():
    from mxeval.data import get_data
    mbpp = get_data("mbxp", "python")
    p = PythonIncrementalParser()
    assert p._get_indentation(mbpp['MBPP/1']["prompt"]) == 4
    assert p._get_indentation(mbpp['MBPP/2']["prompt"]) == 2
    assert p._get_indentation(mbpp['MBPP/8']["prompt"]) == 1


def test_simplications():
    import regex
    simplifications = DFAMaskStore.python_simplifications
    
    # COMMENT 
    reg = simplifications['COMMENT']
    assert regex.match(reg, '# Hello') is not None
    assert regex.match(reg, '""" Foo \n Bar """') is not None
    assert regex.match(reg, "''' Foo \n Bar '''") is not None

    # LONG_STRING
    reg = simplifications['LONG_STRING']
    assert regex.match(reg, '""" Foo \n Bar """') is not None
    assert regex.match(reg, "''' Foo \n Bar '''") is not None
    assert regex.match(reg, '""" Foo \n Bar ') is None
    assert regex.match(reg, "''' Foo \n Bar ") is None

    # STRING
    reg = simplifications['STRING']
    assert regex.match(reg, '"Foo"') is not None
    assert regex.match(reg, "'Foo'") is not None
    assert regex.match(reg, '"Foo') is None
    assert regex.match(reg, "'Foo") is None

    # _NL
    reg = simplifications['_NL']
    assert regex.match(reg, '\n') is not None
    assert regex.match(reg, '\n\n') is not None
    assert regex.match(reg, '\n""" Foo \n Bar """') is not None
    assert regex.match(reg, '\n# Hello!') is not None

    # We are not precise in this case but still sound
    # assert regex.match(reg, '\n""" Foo \n Bar ') is None 

import argparse

if __name__ == '__main__':
    """
        Run all tests by default. In case we only want to run DFAMaskStore object independent tests (as in CI), we can run with the flag --independent
    """
    argparser = argparse.ArgumentParser(description='Run tests for DFAMaskStore object')
    argparser.add_argument('--independent', action='store_true', help='Run only independent tests')
    args = argparser.parse_args()

    # This is just for quick testing while debugging
    # run_ind, run_codegen, run_llama, run_wizard = False, True, False, False
    run_ind, run_codegen, run_llama, run_wizard = True, True, True, True

    # Independent tests
    if run_ind:
        test_ind = [test_simplications]
        common.run_tests(test_ind)

    if args.independent:
        exit(0)

    # Run tests for Llama model
    if run_llama:
        model = 'Llama-7b'
        tokenizer = common.load_tokenizer(model)
        dfa_mask = DFAMaskStore.load_dfa_mask_store(grammar='python', tokenizer=tokenizer, use_cache=True, logger=common.EmptyLogger())
        tests_llama = [test_dfa_mask, test_dfa_mask2, test_dfa_mask3, test_dfa_mask4, test_dfa_mask5, test_dfa_mask6, test_dfa_mask7, test_dfa_mask8, test_dfa_mask9, test_dfa_mask13, test_indent, test_dfa_mask_with_indent]
        common.run_tests(tests_llama)

    # Run tests for Codegen model
    if run_codegen:
        model = 'Salesforce/codegen-350M-multi'
        tokenizer = common.load_tokenizer(model)
        dfa_mask = DFAMaskStore.load_dfa_mask_store(grammar='python', tokenizer=tokenizer, use_cache=True, logger=common.EmptyLogger())
        tests_codegen = [test_dfa_mask10, test_dfa_mask11, test_dfa_mask12]
        # tests_codegen = [test_dfa_mask12]
        common.run_tests(tests_codegen)

    if run_wizard:
        model = 'WizardLM/WizardCoder-1B-V1.0'
        tokenizer = common.load_tokenizer(model)
        dfa_mask = DFAMaskStore.load_dfa_mask_store(grammar='python', tokenizer=tokenizer, use_cache=True, logger=common.EmptyLogger())
        tests_codegen = [test_dfa_mask10, test_dfa_mask11]
        common.run_tests(tests_codegen)
