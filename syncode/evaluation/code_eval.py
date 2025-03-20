import os
import time
import torch
from tqdm import tqdm
from typing import Optional
from syncode import common
from syncode.evaluation.mxeval_evaluation import check_corectness
from syncode.evaluation.mxeval.data import write_jsonl


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
        debug_task_id: Optional[int]=None,
        logger=common.EmptyLogger(),
        num_tasks: Optional[int]=None
        ):
        problems = syncode.dataset.problems

        samples = []
        outputs = []

        assert syncode.mode == 'original' or syncode.parse_output_only == False, "The SynCode flag parse_output_only should be False for code evaluation with grammar mode"

        if syncode.language == "python":
            stop_words = ["\n\n\n"]
        elif syncode.language == "go":
            stop_words = ["\n\n\n"]
        else:
            stop_words = None

        if debug_task_id is None:
            time1 = time.time()
            pbar = tqdm(total=len(problems) * num_samples_per_task)

            # Run evaluation for all tasks
            for task_id in list(problems.keys())[:num_tasks]:
                outputs.append(
                    CodeEval.run_eval_for_task(syncode, num_samples_per_task, format_tabs, problems, samples, task_id, stop_words=stop_words)
                    )
                pbar.update(num_samples_per_task)
            
            pbar.close()
            if out_path is not None: write_jsonl(out_path, samples)
            
            avg_time = (time.time() - time1) / len(problems)
            functional_result = check_corectness(out_path, logger=logger)
            logger.log(f"Functional result: {functional_result}")

            # Also log these results in a separate file
            CodeEval.write_results(syncode, out_path, avg_time, functional_result, num_tasks)
        else: # Debugging a specific task
            debug_task_id = list(problems.keys())[debug_task_id]
            return CodeEval.run_eval_for_task(
                syncode, num_samples_per_task, format_tabs, problems, samples, debug_task_id, logger=logger, stop_words=stop_words
                )
        return outputs

    def run_eval_for_task(syncode, num_samples_per_task, format_tabs, problems, samples, task_id, logger=common.EmptyLogger(), stop_words=None):
        """
        run evaluation for a specific task
        """
        logger.log(f"Running eval for task {task_id}")

        if format_tabs:
            # In this case, we replace 4 spaces with a tab
            prompt = problems[task_id]["prompt"].replace("    ", "\t")
            problems[task_id]["prompt"] = prompt
        else:
            prompt = problems[task_id]["prompt"]

        batch_completions = syncode.model.generate_grammar_constrained_completion(prompt, num_samples_per_task, stop_words=stop_words, return_token_ids=True)
        batch_size = len(batch_completions)
        all_completions = []

        for i, (_, generated_ids, input_ids) in enumerate(batch_completions):
            input_ids_cutoff = input_ids.size(1)

            # We tokenize the whole thing together since tokenizer just the generated_ids messes up with the 
            # indentation and removes the initial whitespaces in some cases
            raw_completion = syncode.model.tokenizer.decode(generated_ids, skip_special_tokens=True)
            grammar_constrainer = syncode.model.logits_processor.grammar_engine

            # Post-processing to filter out using stop word
            if syncode.model.grammar != None and syncode.model.grammar.name == "python":
                completion = CodeEval.postproces_completion_python(syncode.model, i, batch_size, input_ids_cutoff, generated_ids, grammar_constrainer, raw_completion, stop_words)
            elif syncode.model.grammar != None and syncode.model.grammar.name == "go": 
                completion = CodeEval.postproces_completion_go(syncode.model, i, batch_size, raw_completion, generated_ids, grammar_constrainer, input_ids_cutoff)
            else: # TODO: handle the case for other grammars
                completion = raw_completion
                
            result = dict(
                    task_id=task_id,
                    language=problems[task_id]["language"],
                    completion=completion
                )
            samples += [result]
            all_completions.append(completion)

        # Clear the cache
        torch.cuda.empty_cache()
        return all_completions

    def write_results(syncode, out_path, avg_time, functional_result, num_tasks=1):
        """
        Write results to a separate file
        """
        file_path = "results/syncode_results.txt"
        os.makedirs("results", exist_ok=True)
        with open(file_path, "a") as f:
            f.write(f"{syncode.model_name} | {syncode.grammar} | {syncode.dataset} | {syncode.parser} | {syncode.num_samples} | {syncode.mode} | num tasks: {num_tasks}\n")
            f.write(f"Generation args: {syncode.model.gen_args}\n")
            f.write(f"Functional result: {functional_result}\n")
            f.write(f"Output path: {out_path}\n")
            f.write(f"Averge time taken for each task: {avg_time:.2f}s\n")
            f.write("\n")
    
    def postproces_completion_python(hf_model, i, batch_size, input_ids_cutoff, generated_ids, grammar_constrainer, raw_completion, stop_words):        
        generated_output = hf_model.tokenizer.decode(generated_ids[input_ids_cutoff:])

        if all(stop_word not in generated_output for stop_word in stop_words) and hf_model.tokenizer.eos_token_id != generated_ids[-1] and grammar_constrainer is not None:
            # Use when the stop word does not exist in the completion and grammar_constrainer is used
            function_incomplete = [False for _ in range(batch_size)]
            completion = CodeEval.compute_backup_completion(hf_model, grammar_constrainer, function_incomplete, i, raw_completion)
        else:
            completion = raw_completion
        return completion

    def postproces_completion_go(hf_model, i, batch_size, raw_completion, generated_ids, grammar_constrainer, input_ids_cutoff):        
        if hf_model.mode != "original": 
            # When the grammar_constrainer is used
            function_incomplete = [False for _ in range(batch_size)]
            completion = CodeEval.compute_backup_completion(hf_model, grammar_constrainer, function_incomplete, i, raw_completion)

            if function_incomplete[i]:
                completion += "}"

        return completion

    def compute_backup_completion(hf_model, grammar_constrainer, function_incomplete, i, raw_completion):
        if grammar_constrainer.function_ends[i] is not None:
            fn_ends = sorted(list(set(grammar_constrainer.function_ends[i])))
            if len(fn_ends) > 1:
                # if the function end is not None, then the last valid state is the function end
                last_valid_state = fn_ends[1]
                return raw_completion[:last_valid_state]
        
        # otherwise, the last valid state is the last valid state
        function_incomplete[i] = True
        last_valid_state = grammar_constrainer.last_valid_state[i]

        # Use when the stop word does not exist in the completion
        backup_completion = raw_completion[:last_valid_state]
        return backup_completion
    