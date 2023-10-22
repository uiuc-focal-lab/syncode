from synchromesh.synchromesh import is_prefix_valid
from synchromesh.completion_engine import LarkCompletionEngine

comp_engine = LarkCompletionEngine('dict', True)
completion_points = {}
completion_points[''] = comp_engine.complete('')


def test_is_prefix_valid(): 
    s = 'from typing import List\n\n\ndef rescale_to_unit(numbers: List[float]) -> List[float]:\n\t""" Given list of numbers (of at least two elements), apply a linear transform to that list,\n\tsuch that the smallest number will become 0 and the largest will become 1\n\t>>> rescale_to_unit([1.0, 2.0, 3.0, 4.0, 5.0])\n\t[0.0, 0.25, 0.5, 0.75, 1.0]\n\t"""'
    assert is_prefix_valid(comp_engine, completion_points, s) == True

test_is_prefix_valid()