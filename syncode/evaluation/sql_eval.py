from tqdm import tqdm
from mxeval.data import write_jsonl


class SQLEval:
    """
    Run evaluation on SQL dataset
    """
    @staticmethod
    def run_eval(syncode):
        problems = syncode.dataset.problems[:100]
        samples = []
        pbar = tqdm(total=len(problems) * syncode.num_samples)
        results = {}
        assert syncode.num_samples == 1, "SQL evaluation only supports num_samples=1"
        predict_file = syncode.out_path

        if syncode.grammar_decoder is not None:
            syncode.grammar_decoder.parse_output_only = True # Do not parse input+output

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
        from syncode.utils.sql_spider_eval.evaluation import evaluate
        gold_file = "syncode/utils/sql_spider_eval/evaluation_examples/gold_example.txt"
        tables = "syncode/utils/sql_spider_eval/evaluation_examples/examples/tables.json"
        databses = "syncode/utils/sql_spider_eval/databases"
        scores, error_types = evaluate(predict_file, gold_file, databses, etype="all", table=tables, result_jsonl=samples)
        print(f"Scores: {scores['all']}\n Error types: {error_types}")
        write_jsonl(syncode.out_path, samples)
