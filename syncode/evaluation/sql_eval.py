import os
import time
from typing import Optional
from tqdm import tqdm
from syncode.evaluation.mxeval.data import write_jsonl


class SQLEval:
    """
    Class for running evaluation on SQL spider dataset
    """
    @staticmethod
    def run_eval(syncode, out_path: Optional[str], num_tasks: Optional[int]=None, debug_task_id: Optional[int] = None):
        """
        Run evaluation on SQL dataset
        """
        problems = syncode.dataset.problems

        # Run only for num_tasks
        if num_tasks is not None:
            problems = problems[:num_tasks]
        
        samples = []
        pbar = tqdm(total=len(problems) * syncode.num_samples)
        results = {}
        assert syncode.num_samples == 1, "SQL evaluation only supports num_samples=1"
        predict_file = out_path

        if syncode.grammar_decoder is not None:
            syncode.grammar_decoder.parse_output_only = True # Do not parse input+output

        if debug_task_id is not None:
            problems = [problems[debug_task_id]]

        with open(predict_file, 'w') as f:
            for task_id, problem in enumerate(problems):
                results[task_id] = []
                start_time = time.time()
                batch_completions = syncode.model.generate_batch_completion_grammar(
                    problem['prompt'],
                    syncode.num_samples
                    )
                end_time = time.time()
                raw_completion = batch_completions[0]
                completion = syncode.dataset.post_process_answer(raw_completion)

                extract = False
                # If this flag is set try to extract the SQL query from the completion
                if extract:
                    # We consider possibilities where the output is in either ``` {output} ``` or ```sql {output} ``` format
                    if '```' in completion:
                        completion = completion.split('```')[1]
                        if 'sql' in completion:
                            completion = completion.split('sql')[1]
                        print(f"Extracted completion: {completion}")

                res = dict(
                    task_id=task_id,
                    completion=completion,
                    total_tokens=syncode.model.total_tokens,
                    total_time=end_time - start_time
                )
                samples += [res]
                f.write(completion + '\n')
                pbar.update(syncode.num_samples)
        pbar.close()

        # Run evaluation script
        SQLEval.compute_accuracy(samples, predict_file)
        
        if out_path is not None and debug_task_id is None: write_jsonl(out_path, samples)

    @staticmethod
    def compute_accuracy(results_jsonl, predict_file):
        from syncode.utils.sql_spider_eval.evaluation import evaluate

        # Get current dir path
        current_dir = os.path.dirname(os.path.realpath(__file__))

        # Set paths
        gold_file = f"{current_dir}/../utils/sql_spider_eval/evaluation_examples/gold_example.txt"
        tables = f"{current_dir}/..//utils/sql_spider_eval/evaluation_examples/examples/tables.json"
        databses = f"{current_dir}/..//utils/sql_spider_eval/databases"

        scores, error_types = evaluate(predict_file, gold_file, databses, etype="all", table=tables, result_jsonl=results_jsonl)
        print(f"Scores: {[(lvl, scores[lvl]['exec']) for lvl in scores.keys()]}\nError types: {dict(error_types)}\nCounts: {[(lvl, scores[lvl]['count']) for lvl in scores.keys()]}")

        print("Execution accuracy:", scores['all']['exec']) 
        print(f"Compilation error types: {dict(error_types)}")

        # Average token count
        total_tokens = sum([r['total_tokens'] for r in results_jsonl])
        print(f"Average token count: {total_tokens/len(results_jsonl)}")

        # Average time
        total_time = sum([r['total_time'] for r in results_jsonl])
        print(f"Average time: {total_time/len(results_jsonl)}")
        return scores, error_types, results_jsonl
