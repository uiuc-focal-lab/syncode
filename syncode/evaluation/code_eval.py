import os
import time
from tqdm import tqdm
from typing import Optional
from syncode import common
from syncode.evaluation.mxeval_evaluation import check_coorectness
from mxeval.data import write_jsonl


class CodeEval:
    """
    Run evaluation for the code generation model
    """
    @staticmethod
    def run_code_eval(
        syncode, 
        num_samples_per_task: int,
        out_path: Optional[str]=None,
        format_tabs: bool = False,
        debug_task_id: Optional[int] = None,
        logger=common.EmptyLogger()
        ):
        problems = syncode.dataset.problems

        samples = []
        outputs = []
        pbar = tqdm(total=len(problems) * num_samples_per_task)
        if debug_task_id is None:
            time1 = time.time()
            for task_id in problems:
                outputs.append(CodeEval.run_eval_for_task(syncode, num_samples_per_task, format_tabs, problems, samples, pbar, task_id))
            
            if out_path is not None: write_jsonl(out_path, samples)
            
            avg_time = (time.time() - time1) / len(problems)
            functional_result = check_coorectness(out_path, logger=logger)
            logger.log(f"Functional result: {functional_result}")

            # Also log these results in a separate file
            CodeEval.write_results(syncode, out_path, avg_time, functional_result)
        else: # Debugging a specific task
            debug_task_id = list(problems.keys())[debug_task_id]
            return CodeEval.run_eval_for_task(syncode, num_samples_per_task, format_tabs, problems, samples, pbar, debug_task_id, logger=logger)
        return outputs

    def run_eval_for_task(syncode, num_samples_per_task, format_tabs, problems, samples, pbar, task_id, logger=common.EmptyLogger()):
        """
        run evaluation for a specific task
        """
        logger.log(f"Running eval for task {task_id}")

        if format_tabs:
            prompt = problems[task_id]["prompt"].replace("    ", "\t")
        else:
            prompt = problems[task_id]["prompt"]

        batch_completions = syncode.model.generate_batch_completion_grammar(prompt, num_samples_per_task)

        for _, completion in enumerate(batch_completions):
            result = dict(
                    task_id=task_id,
                    language=problems[task_id]["language"],
                    completion=completion
                )
            samples += [result]
        pbar.update(num_samples_per_task)
        return batch_completions

    def write_results(self, out_path, avg_time, functional_result):
        """
        Write results to a separate file
        """
        file_path = "results/syncode_results.txt"
        os.makedirs("results", exist_ok=True)
        with open(file_path, "a") as f:
            f.write(f"{self.model_name} | {self.grammar} | {self.dataset} | {self.parser} | {self.num_samples} | {self.mode}\n")
            f.write(f"Functional result: {functional_result}\n")
            f.write(f"Output path: {out_path}\n")
            f.write(f"Averge time taken for each task: {avg_time:.2f}s\n")
            f.write("\n")