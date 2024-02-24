import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
import syncode.common as common
from syncode.infer import Syncode
from mxeval.data import get_data
from syncode.evaluation import check_correctness_python
import re
#TODO: make this run faster


def test_syntax_mask_humaneval_python():
    sg_mask = Syncode(model = "test", mode = 'grammar_mask', device = 'cpu', do_sample = False, max_new_tokens = 200, dataset = 'humaneval')
    problems = list(get_data('multi-humaneval', 'python').values())

    # test grammar_mask does not cause functional generated code to fail
    for i in [7, 12, 28]:
        assert check_correctness_python(problems[i], sg_mask.infer(task_id= i)[0], timeout=10.0)['result'] == 'passed', f"SynCode Causes Functional Generated Code to Fail for HumanEval/{i}"
    
    # test grammar_mask eliminates syntax errors in generated code
    for i in [25, 81, 84, 105, 107]:
        output = sg_mask.infer(task_id= i)[0]
        assert 'Syntax' not in check_correctness_python(problems[i], output, timeout=10.0)['error_type'], f"Generated Code for HumanEval/{i} has a Syntax Error\n{output}"

def test_custom_grammar_string():
    grammar = """
        start: expr

        ?expr: term
            | expr "+" term      -> add
            | expr "-" term      -> subtract
            | expr "*" term      -> multiply
            | expr "/" term      -> divide
            | expr "=" term      -> equal

        ?term: NUMBER          -> number
            | "(" expr ")"

        %import common.NUMBER
        %import common.WS
        %ignore WS
    """
    # model_name = "microsoft/phi-2"
    model_name = "Salesforce/codegen-350M-multi"
    sg_mask = Syncode(model = model_name, mode='grammar_mask', device='cpu', do_sample=False, max_new_tokens=20, grammar=grammar, parse_prompt=False, dev_mode=True)

    output = sg_mask.infer("What is 2+2?")
    # assert 
    output = sg_mask.infer('What is 7 multiplied by 8?')
    # assert len(output) == 0 or re.match(r'^[\d()+\-*/\n ]+$', output, flags=re.DOTALL), f"{output} is syntactically incorrect"
    output = sg_mask.infer('What is square root of 64?')
    # ['2\n\n**\n\n**\n\n**\n\n**\n\n**\n\n**\n']
    # assert sg_mask.infer("1 + 1 = ")[0] == '2'

    # '0.\n\n**\n\n**\n\n**\n\n**\n\n**\n\n**'
    
    

tests = [test_syntax_mask_humaneval_python, test_custom_grammar_string]
tests = [test_custom_grammar_string]
common.run_tests(tests)