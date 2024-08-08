import time
from typing import Optional
from tqdm import tqdm
from syncode import common
from syncode.evaluation.mxeval_evaluation import compute_pass_at_k
from mxeval.data import write_jsonl


class MathEval:
    """
    Run evaluation on math question-answer dataset 
    """
    @staticmethod
    def run_math_eval(syncode, out_path: Optional[str], debug_task_id=None, logger=common.EmptyLogger()):
        problems = syncode.dataset.problems
        if debug_task_id is not None:
            problems = [problems[debug_task_id]]
        samples = []
        pbar = tqdm(total=len(problems) * syncode.num_samples)
        time1 = time.time()
        results = {} # result maps task_id to a list of (completion_id, result) tuples for each sample

        for task_id, problem in enumerate(problems):
            results[task_id] = []
            batch_completions = syncode.model.generate_batch_completion_grammar(
                problem['question'], 
                syncode.num_samples
                )
            for completion_id, raw_completion in enumerate(batch_completions):
                completion = syncode.dataset.post_process_answer(raw_completion)
                logger.log(f"\n\nProblem: {problem}\nCompletion: {completion}\n")
                true_answer = float(problem['answer'].split('#')[-1].replace(',', ''))
                llm_answer = None
                try:
                    ans = completion.split('\n\n')[0]
                    ans.replace(',', '')
                    llm_answer = float(ans.split('#')[-1])
                except:
                    pass
                logger.log(f"True answer: {true_answer},\nLLM answer: {llm_answer}")
                passed = (true_answer == llm_answer)
                res = dict(
                    task_id=task_id,
                    completion=completion,
                    passed=passed,
                )
                samples += [res]
                results[task_id].append((completion_id, res))          
            pbar.update(syncode.num_samples)

        if out_path is not None: write_jsonl(out_path, samples)
        pass_at_k = compute_pass_at_k(results)

        # Log result and time
        avg_time = (time.time() - time1) / len(problems)
        print(f"Result: {pass_at_k}")
        logger.log(f"Result: {pass_at_k}")
        return samples
    