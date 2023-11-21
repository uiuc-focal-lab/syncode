import argparse
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import sys
import traceback
from typing import List, Union, Iterable, Dict
import itertools
import os
import numpy as np
import time
import tqdm
from typing import Optional, Callable, Dict
import multiprocessing
import subprocess
import re

from mxeval.data import read_problems, stream_jsonl, write_jsonl, get_metadata
from mxeval.execution import swallow_io, time_limit, TimeoutException, create_tempdir, reliability_guard, setup_base_path
from mxeval.evaluation import estimate_pass_at_k, get_execute_function


def evaluate_functional_correctness(
    sample_file: str,
    k: List[int] = [1, 10, 100],
    n_workers: int = os.cpu_count() - 1,
    timeout: float = 10.0,
    problem_file: str = '',
):
    """
    Evaluates the functional correctness of generated samples, and writes
    results to f"{sample_file}_results.jsonl"
    """

    if type(problem_file) is not dict:
        problems = read_problems(problem_file)
    else:
        print("Skip reading problems -- using problem_file (dict) as problems")
        problems = problem_file
    
    error_types = {}

    # see execution.py for details
    # Check the generated samples against test suites.
    check_correctness_function_map = {
        "python": check_correctness,
        "go": check_correctness_go
    }
    seed = int(time.time() * 1000000) % 1000000
    np.random.seed(seed=seed)  # microsecond

    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        futures = []
        completion_id = Counter()
        n_samples = 0
        results = defaultdict(list)

        print("Reading samples...")
        for sample in tqdm.tqdm(stream_jsonl(sample_file)):
            task_id = sample["task_id"]
            completion = sample["completion"]
            args = (problems[task_id], completion, timeout, completion_id[task_id])
            language = sample["language"]
            check_correctness_function = check_correctness_function_map[language]
            future = executor.submit(check_correctness_function, *args)
            futures.append(future)
            completion_id[task_id] += 1
            n_samples += 1

        assert len(completion_id) == len(problems), "Some problems are not attempted."

        print("Running test suites...")
        i = 0
        for future in tqdm.tqdm(as_completed(futures), total=len(futures)):
            result = future.result()  # this is the execution stage
            results[result["task_id"]].append((result["completion_id"], result))
            i += 1

            if result["error_type"] not in error_types:
                error_types[result["error_type"]] = 0
            error_types[result["error_type"]] += 1

    print(error_types)

    # common code for all languages
    # Calculate pass@k.
    total, correct = [], []
    for result in results.values():
        result.sort()
        passed = [r[1]["passed"] for r in result]
        total.append(len(passed))
        correct.append(sum(passed))
    total = np.array(total)
    correct = np.array(correct)

    ks = k
    pass_at_k = {
        f"pass@{k}": estimate_pass_at_k(total, correct, k).mean()
        for k in ks
        if (total >= k).all()
    }

    # Finally, save the results in one file:
    def combine_results():
        for sample in stream_jsonl(sample_file):
            task_id = sample["task_id"]
            result = results[task_id].pop(0)
            sample["result"] = result[1]["result"]
            sample["passed"] = result[1]["passed"]
            sample["time_elapsed"] = result[1]["time_elapsed"]
            sample["error_type"] = result[1]["error_type"]
            yield sample

    out_file = sample_file + "_results.jsonl"
    print(f"Writing results to {out_file}...")
    write_jsonl(out_file, tqdm.tqdm(combine_results(), total=n_samples))

    return pass_at_k



def check_correctness(
    problem: Dict, completion: str, timeout: float, completion_id: Optional[int] = None
) -> Dict:
    """
    Evaluates the functional correctness of a completion by running the test
    suite provided in the problem.
    :param completion_id: an optional completion ID so we can match
        the results later even if execution finishes asynchronously.
    """

    def unsafe_execute():

        with create_tempdir():

            # These system calls are needed when cleaning up tempdir.
            import os
            import shutil

            rmtree = shutil.rmtree
            rmdir = os.rmdir
            chdir = os.chdir

            # Disable functionalities that can make destructive changes to the test.
            reliability_guard()

            prompt = problem["prompt"].replace("\t", "    ")

            # Construct the check program and run it.
            check_program = (
                prompt
                + completion
                + "\n"
                + problem["test"]
                + "\n"
                + f"check({problem['entry_point']})"
            )
            try:
                exec_globals = {}
                with swallow_io():
                    with time_limit(timeout):
                        exec(check_program, exec_globals)
                print('Passed')
                error_types.append('No Error')
                result.append("passed")
            except AssertionError as e:
                _, _, tb = sys.exc_info()
                traceback.print_tb(tb) # Fixed format
                tb_info = traceback.extract_tb(tb)
                filename, line, func, text = tb_info[-1]
                error_types.append(type(e).__name__)
                print('An assertion error occurred on line {} in statement {}.{}.{}'.format(line, text, func, filename))
                print(e)
            except TimeoutException:
                result.append("timed out")
                error_types.append(type(e).__name__)
                print('Timeout!')
            except SyntaxError as e:
                print('Syntax Error!')
                error_types.append(type(e).__name__)
            except Exception as e:
                tb = traceback.format_exc()
                error_types.append(type(e).__name__)
                result.append(f"failed: {e}")
                print('Failed!')

            # Needed for cleaning up.
            shutil.rmtree = rmtree
            os.rmdir = rmdir
            os.chdir = chdir

    manager = multiprocessing.Manager()
    result = manager.list()
    error_types = manager.list()

    start = time.time()
    p = multiprocessing.Process(target=unsafe_execute)
    p.start()
    p.join(timeout=timeout + 1)
    if p.is_alive():
        p.kill()
    elapsed = 1000.0 * (time.time() - start)

    if not result:
        result.append("timed out")
    
    if not error_types:
        error_types.append('Timeout')

    return dict(
        task_id=problem["task_id"],
        passed=result[0] == "passed",
        result=result[0],
        completion_id=completion_id,
        time_elapsed=elapsed,
        error_type = error_types[0]
    )

def check_correctness_helper(
    problem: Dict,
    completion: str,
    timeout: float,
    completion_id: Optional[int] = None,
    verbose=False,
    language=None,
    extension=None,
    subprocess_command_lambda=None,
    compile_timeout=100,
    compile_command_lambda=None,
    extra_cleanup=None,
    cwd=None,
):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    entire_string = problem["prompt"] + completion + problem["test"]

    language_dirname = f"{language}_exec_eval"

    base_path = setup_base_path(current_dir, language_dirname, extension)
    path = base_path + f"{extension}"

    if cwd is not None:
        cwd = os.path.dirname(base_path)
    with open(path, "w") as f:
        f.write(entire_string)
    try:
        if compile_command_lambda is not None:
            compile_result = subprocess.run(
                compile_command_lambda(base_path),
                timeout=int(compile_timeout),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd,
            )
            compiled = compile_result.returncode == 2 if language == "typescript" else compile_result.returncode == 0
        else:
            compiled = True

        if compiled:
            start = time.time()
            exec_result_run = subprocess.run(
                subprocess_command_lambda(base_path),
                timeout=int(timeout),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd,
            )
            elapsed = 1000.0 * (time.time() - start)
            if verbose:
                print("exec result run", exec_result_run)
            if 'syntax error' in exec_result_run.stderr: # Works for go
                error_type = 'SyntaxError'
            elif exec_result_run.returncode != 0:
                error_type = 'OtherError'
            else:
                error_type = 'NoError'
            passed = exec_result_run.returncode == 0
            message = exec_result_run.stderr
        else:
            passed, message, error_type, elapsed = False, compile_result.stderr, compile_result.stderr, None

    except Exception as e:
        if verbose:
            print(f"error occurred when running test cases: {e}")
        message = str(e)
        error_type = type(e).__name__
        passed, elapsed, compiled = False, None, False

    # clean up
    try:
        os.remove(path)
    except Exception as e:
        if verbose:
            print(f"Error trying to clean up file: {e}")
    try:
        if extra_cleanup is not None:
            extra_remove_path = extra_cleanup(base_path)
            assert isinstance(extra_remove_path, str)
            os.remove(extra_remove_path)
    except Exception as e:
        if verbose:
            print(f"Error trying to clean up file: {e}")

    # get result
    return dict(
        task_id=problem["task_id"],
        passed=passed,
        result=message,
        completion_id=completion_id,
        time_elapsed=elapsed,
        compiled=compiled,
        error_type = error_type
    )

def check_correctness_go(
    problem: Dict,
    completion: str,
    timeout: float,
    completion_id: Optional[int] = None,
    verbose=False,
):
    return check_correctness_helper(
        problem=problem,
        completion=completion,
        timeout=timeout,
        completion_id=completion_id,
        verbose=verbose,
        language="go",
        extension=".go",
        subprocess_command_lambda=lambda x: ["go", "run", f"{x}.go"],
    )

def get_datafile(dataset="mbxp", language="python"):
  metadata, datadir = get_metadata(dataset, metadata_type="problem")
  if language.lower() not in metadata:
    raise ValueError(f"Language {language} not found in metadata file")
  datafile = metadata[language.lower()]
  return os.path.join(datadir, datafile)


# Take the filename as input
def compare(get_datafile, filename, language, dataset):
    problem_file=get_datafile(dataset, language)
    filename_original = filename.replace("grammar_mask", "original")

    count_original = 0
    count_grammar_mask = 0
    count_original_unique = 0
    count_grammar_mask_unique = 0

    def print_comparison(p, c1, c2, task_id):
        print('-'*80)
        print(f"Task ID: {task_id}")
        print('Prompt:')
        print(p["prompt"])
        print('Original Completion:')
        print(c1["completion"])
        print('Result:', c1["result"])
        print('Error Type:', c1["error_type"])
        print('Grammar Mask Completion:')
        print(c2["completion"])
        print('Result:', c2["result"])
        print('Error Type:', c2["error_type"])
        print(repr(p['prompt']))
        print(repr(c2['completion']))
        print('-'*80)

    for p, c1, c2 in zip(tqdm.tqdm(stream_jsonl(problem_file)), tqdm.tqdm(stream_jsonl(filename_original)), tqdm.tqdm(stream_jsonl(filename))):
        task_id = c1["task_id"]
        if c1['passed'] != c2['passed']:
            # print_comparison(p, c1, c2, task_id)
            pass
        
        if c2['error_type'] == 'TypeError':
            print_comparison(p, c1, c2, task_id)

        if c1['passed'] and not c2['passed']:
            # print_comparison(p, c1, c2, task_id)
            count_original_unique += 1
        if c2['passed'] and not c1['passed']:
            count_grammar_mask_unique += 1
        if c1['passed']:
            count_original += 1
        if c2['passed']:
            count_grammar_mask += 1

    print(f"Original: {count_original}")
    print(f"Grammar Mask: {count_grammar_mask}")
    print(f"Original unique: {count_original_unique}")
    print(f"Grammar Mask unique: {count_grammar_mask_unique}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", help="Enter the filename")
    parser.add_argument("--compare", help="comparison mode compares results of original and grammar_mask modes", action="store_true")
    args = parser.parse_args()
    filename = args.filename
    language = "go"
    dataset = "mbxp"
    if re.search(r"python", filename,):
        language = "python"
    if re.search( r"humaneval", filename):
        dataset = "multi-humaneval"
    elif re.search(r"mathqa", filename):
        dataset = "mathqa-x"
    
    if args.compare:
        compare(get_datafile, filename, language, dataset)
    else:
        results = evaluate_functional_correctness(filename, problem_file=get_datafile(dataset, language))
        print(results)
