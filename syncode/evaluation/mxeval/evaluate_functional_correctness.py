# Original Copyright 2021 OpenAI under MIT License.
# Modifications Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

import sys
import os

import fire
from syncode.evaluation.mxeval.data import HUMAN_EVAL
from syncode.evaluation.mxeval.evaluation import evaluate_functional_correctness


def entry_point(
    sample_file: str,
    problem_file: str = HUMAN_EVAL,
    k: tuple = (1, 10, 100, 1000),  # from command line, use '1,10,100' for example
    n_workers: int = os.cpu_count() - 1,
    timeout: float = 15.0,
):
    """
    Evaluates the functional correctness of generated samples, and writes
    results to f"{sample_file}_results.jsonl"
    """
    print(f"\n\nEvaluating {sample_file}")
    k = list(map(int, k))
    results = evaluate_functional_correctness(
        sample_file, k, n_workers, timeout, problem_file
    )
    with open(sample_file + "_passatk.json", "w") as f:
        f.write(str(results))
    print(results)


def main():
    fire.Fire(entry_point)


sys.exit(main())
