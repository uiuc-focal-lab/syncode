import sys, os
from typing import Dict
import torch
from transformers import BatchEncoding
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
import common
from infer import Syncode
from mxeval.data import get_data
from evaluation import check_correctness_python, check_correctness_go
#TODO: make this run faster


def test_syntax_mask_humaneval_python():
    sg_mask = Syncode(model = "test", mode = 'grammar_mask', device = 'cpu', do_sample = False, max_new_tokens = 200, dataset = 'humaneval')
    problems = list(get_data('multi-humaneval', 'python').values())

    #test grammar_mask does not cause functional generated code to fail
    for i in [7, 12, 28]:
        assert check_correctness_python(problems[i], sg_mask.infer(task_id= i)[0], 10.0)['result'] == 'passed'
    
    #test grammar_mask eliminates syntax errors in generated code
    for i in [25, 81, 84, 105, 107]:
        assert 'Syntax' not in check_correctness_python(problems[i], sg_mask.infer(task_id= i)[0], 10.0)['error_type']
    
    
tests = [test_syntax_mask_humaneval_python]
common.run_tests(tests)