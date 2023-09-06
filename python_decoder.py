import torch
from transformers import LogitsProcessor

class PythonDecoder(LogitsProcessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:
        return scores

# tokens are here: https://github.com/python/cpython/blob/3.11/Lib/token.py
from tokenize import tokenize
from io import BytesIO
s = 'print("Hello world")'
g = tokenize(BytesIO(s.encode('utf-8')).readline)

for toknum, tokval, _, _, _ in g:
    print(toknum, tokval)