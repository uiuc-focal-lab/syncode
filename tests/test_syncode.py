import unittest
import sys, os, re
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
from syncode.infer import Syncode
from mxeval.data import get_data
from syncode.evaluation.mxeval_evaluation import check_correctness_python

class TestSyncode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Assuming Syncode and get_data are set up correctly in your environment
        cls.sg_mask = Syncode(model="test", mode='grammar_mask', device='cpu', do_sample=False, max_new_tokens=200, grammar='python')
        cls.problems = list(get_data('multi-humaneval', 'python').values())
        
        cls.sg_mask_instruct = Syncode(model="test-instruct", mode='grammar_mask', device='cpu', do_sample=False, max_new_tokens=20, grammar=cls.custom_grammar())
    
    @staticmethod
    def custom_grammar():
        return """
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

    def test_syntax_mask_humaneval_python(self):
        # Test grammar_mask does not cause functional generated code to fail
        for i in [7, 12, 28]:
            result = check_correctness_python(self.problems[i], self.sg_mask.evaluate(dataset='humaneval', task_id=i)[0], timeout=10.0)['result']
            self.assertEqual(result, 'passed', f"SynCode Causes Functional Generated Code to Fail for HumanEval/{i}")
        
        # Test grammar_mask eliminates syntax errors in generated code
        for i in [25, 81, 84, 105, 107]:
            output = self.sg_mask.evaluate(dataset='humaneval', task_id=i)[0]
            error_type = check_correctness_python(self.problems[i], output, timeout=10.0)['error_type']
            self.assertNotIn('Syntax', error_type, f"Generated Code for HumanEval/{i} has a Syntax Error\n{output}")

    def test_custom_grammar_string(self):
        output = self.sg_mask_instruct.infer('7 * ')[0]
        self.assertTrue(re.match(r'^[\d()+\-*/\n ]+$', output, flags=re.DOTALL), f"{output} is syntactically incorrect")
