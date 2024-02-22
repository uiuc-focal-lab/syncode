import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
import common
from infer import Syncode
from mxeval.data import get_data
from evaluation import check_correctness_python
import re
#TODO: make this run faster


def test_syntax_mask_humaneval_python():
    sg_mask = Syncode(model = "test", mode = 'grammar_mask', device = 'cpu', do_sample = False, max_new_tokens = 200, dataset = 'humaneval')
    problems = list(get_data('multi-humaneval', 'python').values())

    # test grammar_mask does not cause functional generated code to fail
    for i in [7, 12, 28]:
        assert check_correctness_python(problems[i], sg_mask.infer(task_id= i)[0], 10.0)['result'] == 'passed'
    
    # test grammar_mask eliminates syntax errors in generated code
    for i in [25, 64, 81, 84, 105, 107]:
        assert 'Syntax' not in check_correctness_python(problems[i], sg_mask.infer(task_id=i)[0], 10.0)['error_type']

def test_custom_grammar_string():
    grammar = """
        start: expr
        ?expr: term
            | expr "+" term  -> add
            | expr "-" term  -> subtract

        ?term: factor
            | term "*" factor  -> multiply
            | term "/" factor  -> divide

        ?factor: NUMBER        -> number
            | "(" expr ")"

        %import common.NUMBER
        %import common.WS
        %ignore WS
    """
    sg_mask = Syncode(model = "test-instruct", mode = 'grammar_mask', device = 'cpu', do_sample = False, max_new_tokens = 50, grammar = grammar)
    # assert sg_mask.infer("1 + 1 = ")[0][0] == '2'
    # assert sg_mask.infer("4 * 0 = ")[0][0] == '0'
    output = sg_mask.infer('7 * ')
    assert re.match(r'^[\d()+\-*\/]+$', output)

tests = [test_syntax_mask_humaneval_python, test_custom_grammar_string]
common.run_tests(tests)