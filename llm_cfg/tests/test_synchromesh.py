"""
This file contains miscellaneous tests for the LLM CFG project
"""
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')
import copy
from common import run_tests
from synchromesh.synchromesh import is_prefix_valid
from synchromesh.completion_engine import LarkCompletionEngine

def setup():
    comp_engine = LarkCompletionEngine('dict', True)
    completion_points = {}
    completion_points[''] = comp_engine.complete('')
    return comp_engine, completion_points

def test_is_prefix_valid(): 
    comp_engine, completion_points = setup()
    s = 'from typing import List\n\n\ndef rescale_to_unit(numbers: List[float]) -> List[float]:\n\t""" Given list of numbers (of at least two elements), apply a linear transform to that list,\n\tsuch that the smallest number will become 0 and the largest will become 1\n\t>>> rescale_to_unit([1.0, 2.0, 3.0, 4.0, 5.0])\n\t[0.0, 0.25, 0.5, 0.75, 1.0]\n\t"""'
    assert is_prefix_valid(comp_engine, completion_points, s) == True

def test_is_prefix_valid2(): 
    comp_engine, completion_points = setup()
    s = 'from typing import List\n\n\ndef rescale_to_unit(numbers: List[float]) -> List[float]:\n\t""" Given list of numbers (of at least two elements), apply a linear transform to that list,\n\tsuch that the smallest number will become 0 and the largest will become 1\n\t>>> rescale_to_unit([1.0, 2.0, 3.0, 4.0, 5.0])\n\t[0.0, 0.25, 0.5, 0.75, 1.0]\n\t"""\n\tfor i in x: # this is'
    assert is_prefix_valid(comp_engine, completion_points, s) == True

def test_is_prefix_valid3(): 
    comp_engine, completion_points = setup()
    s = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\t""" Check if in given list of numbers, are any two numbers closer to each other than\n\tgiven threshold.\n\t>>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n\tFalse\n\t>>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n\tTrue\n\t"""\n\tfor i in x\n\t\t'
    assert is_prefix_valid(comp_engine, completion_points, s) == False

def test_is_prefix_valid4():
    # This is testing if the completion engine state is soundly maintened across multiple calls to is_prefix_valid
    comp_engine, completion_points = setup()
    s1 = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\tfor i in r'
    assert is_prefix_valid(comp_engine, copy.copy(completion_points), s1) == True

    s2 = 'from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n\tfor i in range'
    assert is_prefix_valid(comp_engine, completion_points, s2) == True

tests = [test_is_prefix_valid, test_is_prefix_valid2, test_is_prefix_valid3, test_is_prefix_valid4]
run_tests(tests)
