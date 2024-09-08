import os
from typing import Optional
from tqdm import tqdm
from mxeval.data import write_jsonl


class SQLEval:
    """
    Run evaluation on SQL dataset
    """
    @staticmethod
    def run_eval(syncode, out_path: Optional[str], debug_task_id: Optional[int] = None):
        problems = syncode.dataset.problems[:100]
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
                batch_completions = syncode.model.generate_batch_completion_grammar(
                    problem['prompt'],
                    syncode.num_samples
                    )
                raw_completion = batch_completions[0]
                completion = syncode.dataset.post_process_answer(raw_completion)
                res = dict(
                    task_id=task_id,
                    completion=completion,
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
        print(f"Scores: {[(lvl, scores[lvl]['exec']) for lvl in scores.keys()]}\nError types: {error_types}\nCounts: {[(lvl, scores[lvl]['count']) for lvl in scores.keys()]}")
        return scores, error_types, results_jsonl
