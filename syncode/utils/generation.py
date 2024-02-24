from transformers import (
    PreTrainedModel,
    PreTrainedTokenizer,
)
import typing
from typing import Iterable
BatchGenerator = typing.Callable[
    [PreTrainedModel, PreTrainedTokenizer, str, int], Iterable[str]
]

# reference: https://github.com/declare-lab/instruct-eval/blob/main/human_eval/main.py#L35
def filter_code(completion: str, extra_stop_word="\n\n") -> str:
    # The program tends to overwrite, we only take the first function 
    completion = completion.lstrip("\n")
    return completion.split(extra_stop_word)[0]


def fix_indents(text: str) -> str:
    return text.replace("\t", "    ")


def split_batch(samples: Iterable[str], size=4):
    mini_batches = []

    for i in range(0, len(samples), size):
        mini_batches.append(samples[i : i + size])

    return mini_batches
