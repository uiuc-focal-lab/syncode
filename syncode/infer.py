import time, os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import fire
import syncode.common as common
from syncode.language_model import HuggingFaceModel
from transformers import LogitsProcessorList
from syncode.grammar_decoder import GrammarDecoder
from typing import Optional, Literal
from mxeval.data import write_jsonl
from tqdm import tqdm
from syncode.evaluation import check_coorectness, compute_pass_at_k
from syncode.parsers.grammars import Grammar
from syncode.dataset import Dataset


def compile_and_run(model, mode="original", quantize=True, device="cuda", num_samples=1, grammar=None, dataset="input", num_few_shot=0, chat_mode=False, dev_mode=False, log_level=1, new_mask_store=False, parser="lalr", task_id=None, **kwargs):
    sc = Syncode(model, mode=mode, quantize=quantize, device=device, num_samples=num_samples, grammar=grammar, dataset=dataset, num_few_shot=num_few_shot, chat_mode=chat_mode, dev_mode=dev_mode, log_level=log_level, new_mask_store=new_mask_store, parser=parser, task_id=task_id, **kwargs)
    sc.infer(task_id=task_id)

class Syncode:
    """Syncode class for running inference on a model
    Args:
        mode (str, optional): Mode for inference. Defaults to "original".
        model (str): Model id for huggingface model hub or model name if stored locally.
        quantize (bool, optional): Quantize model. Defaults to True.
        device (str, optional): Device to use. Defaults to "cuda".
        num_samples (int, optional): Number of samples. Defaults to 1.
        grammar (str, optional): Language. Defaults to "input". "input" is used for user input. 
            other options currently supported are "python", "go", "calc"
        dataset (str, optional): Dataset. Defaults to "humaneval".
        new_mask_store (bool, optional): Use new DFA mask store. Defaults to False.
        num_few_shot (int, optional): Number of examples for few shot prompting. Defaults to 0.
        chat_mode (bool, optional): Parse only the (output) and not (prompt+output) in chat mode. Defaults to False.
        dev_mode (bool, optional): Development mode. Defaults to False.
        log_level (int, optional): Log level. Defaults to 2. 0 for no logs, 1 for minimal logs, 2 for all logs including time.
        parser (str, optional): Parser to use. Defaults to "lalr".
        task_id (int, optional): For debugging a specific task. Defaults to None.

        List of currently tested models:
        Llama models: "Llama-7b", "CodeLlama-7b", "CodeLlama-7b-Python", "Llama-13b"
        CodeGen models: "Salesforce/codegen-350M-multi", "Salesforce/codegen2-1b"
        Bigcode models: "bigcode/starcoderbase-1b", "bigcode/santacoder" (1.1b WIP)
        WizardLM models: "WizardLM/WizardCoder-1B-V1.0"
    """
    def __init__(
        self, 
        model: str,
        mode: Literal["original", "grammar_mask"] = "original",
        quantize: bool = True,
        device: str = "cuda",
        num_samples: int = 1,
        grammar: Optional[str] = None,
        dataset: Literal["mbxp", "humaneval", "mathqa-x", "input"] = "input",
        num_few_shot: int = 0,
        chat_mode: bool = False,
        dev_mode: bool = False,
        log_level: int = 1,
        new_mask_store: bool = False,
        parser: Literal["lr", "lalr"] = "lalr",
        task_id: Optional[int] = None,
        **kwargs
    ):  
        # Check inputs
        assert mode in ["original", "grammar_mask"]
        gen_kwargs = {'max_length', 'max_new_tokens', 'min_length', 'min_new_tokens', 'early_stopping', 'do_sample', 'num_beams', 'use_cache', 'temperature', 'top_k', 'top_p', 'num_return_sequences', 'pad_token_id', 'eos_token_id'}
        invalid_kwargs = kwargs.keys() - gen_kwargs
        assert invalid_kwargs == set(), f"Invalid arguments {invalid_kwargs}"

        # Set attributes
        self.mode = mode
        self.model_name = model
        self.quantize = quantize
        self.device = device
        self.num_samples = num_samples
        self.new_mask_store = new_mask_store
        self.num_few_shot = num_few_shot
        self.parser = parser
        self.chat_mode = chat_mode

        # Set the grammar
        self.grammar = Grammar(grammar) if self.mode == 'grammar_mask' else None

        # Load the dataset
        self.dataset = Dataset(dataset, language=grammar, num_few_shot=num_few_shot)

        # Load model
        model = common.load_model(self.model_name, device)
        tokenizer = common.load_tokenizer(self.model_name)
        
        # Setup output directory
        out_dir, self.out_path = self.get_output_path()
        self.logger = common.Logger(self.num_samples, mode, parser, out_dir, log_level=log_level, task_id=task_id)
        
        # Initialize logit processors
        logit_processors = None
        self.grammar_decoder = None
        
        if self.mode == 'grammar_mask':
            self.grammar_decoder = GrammarDecoder(
                self.grammar, 
                tokenizer=tokenizer, 
                logger=self.logger, 
                use_cache=(not self.new_mask_store), 
                chat_mode=chat_mode,
                num_samples=self.num_samples, 
                dev_mode=dev_mode,
                parser=parser
                )
            logit_processors = LogitsProcessorList([self.grammar_decoder])

        # Set LLM generation args e.g. max_new_tokens, do_sample, etc.
        self.set_generation_args(kwargs, tokenizer)

        self.model = HuggingFaceModel(
            model, 
            grammar=self.grammar,
            logger=self.logger, 
            tokenizer=tokenizer, 
            device=device, 
            logit_processors=logit_processors, 
            mode=self.mode, 
            **kwargs
            )

    def infer(self, prompt=None, task_id=None):
        if self.logger.is_closed:
            self.logger.open()

        if self.dataset.type == "code": 
            output = CodeEval.run_code_eval(self, self.num_samples, self.out_path, format_tabs=True, debug_task_id=task_id)
        elif self.dataset.type == "math":
            output = MathEval.run_math_eval(self, debug_task_id=task_id)
        elif self.dataset.type == "sql":
            output = SQLEval.run_eval(self)
        elif self.dataset.type == "input":
            output = self.user_input(prompt)
        else:
            raise ValueError(f"Dataset type {self.dataset.type} not supported")
        self.logger.close()
        return output

    def get_output_path(self):
        out_dir = f"results/{self.model_name}/{self.grammar}/{self.dataset}/"
        out_path = out_dir + 'samples_' + str(self.num_samples) + '_mode_' + str(self.mode) + "_eval.jsonl"
        os.makedirs(out_dir, exist_ok=True)
        return out_dir,out_path
    
    def set_generation_args(self, kwargs, tokenizer):
        kwargs['max_new_tokens'] = kwargs.get('max_new_tokens', 200)
        kwargs['do_sample'] = kwargs.get('do_sample', False)
        kwargs['use_cache'] = kwargs.get('use_cache', True)
        kwargs['eos_token_id'] = kwargs.get('eos_token_id', tokenizer.eos_token_id)
        kwargs['pad_token_id'] = kwargs.get('pad_token_id', tokenizer.eos_token_id) # model has no pad token
        if kwargs['do_sample'] or self.num_samples > 1: # If sampling, set temperature, top_k, top_p
            kwargs['temperature'] = kwargs.get('temperature', 0.2)
            kwargs['top_k'] = kwargs.get('top_k', self.num_samples)
            kwargs['top_p'] = kwargs.get('top_p', 0.95)
            print(f"Generation args: {kwargs}")

    def user_input(self, prompt):
        """
        Run user input on the model with grammar mask
        """
        if prompt:
            if self.grammar_decoder is not None: # TODO: Remove this check
                    self.grammar_decoder.reset()
            if self.chat_mode:
                return self.model.generate_chat_completion_grammar(prompt)
            else:
                return self.model.generate_batch_completion_grammar(prompt, self.num_samples)
        
        else:
            while True:
                if self.grammar_decoder is not None:
                    self.grammar_decoder.reset()

                prompt = input('Enter prompt: ')
                prompt = prompt.replace('\\n', '\n').replace('\\"', '\"').replace('\\t', '\t').replace("\\'", "\'").replace('\\b', '\b').replace('\\r', '\r') if self.grammar.name == 'python' else prompt
                if prompt == "exit":
                    break
                batch_completions = self.model.generate_batch_completion_grammar(prompt, self.num_samples)
                for i, completion in enumerate(batch_completions):
                    print(prompt + completion)

class CodeEval:
    """
    Run evaluation for the code generation model
    """
    @staticmethod
    def run_code_eval(
        syncode, 
        num_samples_per_task: int,
        out_path: str,
        format_tabs: bool = False,
        debug_task_id: Optional[int] = None
        ):
        problems = syncode.dataset.problems

        samples = []
        outputs = []
        pbar = tqdm(total=len(problems) * num_samples_per_task)
        if debug_task_id is None:
            time1 = time.time()
            for task_id in problems:
                outputs.append(CodeEval.run_eval_for_task(syncode, num_samples_per_task, format_tabs, problems, samples, pbar, task_id))
            write_jsonl(out_path, samples)
            avg_time = (time.time() - time1) / len(problems)
            syncode.logger.log_time(f"Averge time taken for each task: {avg_time:.2f}s")
            functional_result = check_coorectness(out_path, logger=syncode.logger)
            syncode.logger.log(f"Functional result: {functional_result}")

            # Also log these results in a separate file
            CodeEval.write_results(syncode, out_path, avg_time, functional_result)
        else: # Debugging a specific task
            debug_task_id = list(problems.keys())[debug_task_id]
            return CodeEval.run_eval_for_task(syncode, num_samples_per_task, format_tabs, problems, samples, pbar, debug_task_id)
        return outputs

    def run_eval_for_task(syncode, num_samples_per_task, format_tabs, problems, samples, pbar, task_id):
        """
        run evaluation for a specific task
        """
        syncode.logger.log(f"Running eval for task {task_id}")
        if syncode.grammar_decoder is not None:
            syncode.grammar_decoder.reset()

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


class MathEval:
    """
    Run evaluation on math question-answer dataset 
    """
    @staticmethod
    def run_math_eval(syncode, debug_task_id=None):
        problems = syncode.dataset.problems
        if debug_task_id is not None:
            problems = [problems[debug_task_id]]
        samples = []
        pbar = tqdm(total=len(problems) * syncode.num_samples)
        time1 = time.time()
        results = {} # result maps task_id to a list of (completion_id, result) tuples for each sample

        for task_id, problem in enumerate(problems):
            if syncode.grammar_decoder is not None:
                syncode.grammar_decoder.reset()
            results[task_id] = []
            batch_completions = syncode.model.generate_batch_completion_grammar(
                problem['question'], 
                syncode.num_samples
                )
            for completion_id, raw_completion in enumerate(batch_completions):
                completion = syncode.dataset.post_process_answer(raw_completion)
                syncode.logger.log(f"\n\nProblem: {problem}\nCompletion: {completion}\n")
                true_answer = float(problem['answer'].split('#')[-1].replace(',', ''))
                llm_answer = None
                try:
                    ans = completion.split('\n\n')[0]
                    ans.replace(',', '')
                    llm_answer = float(ans.split('#')[-1])
                except:
                    pass
                syncode.logger.log(f"True answer: {true_answer},\nLLM answer: {llm_answer}")
                passed = (true_answer == llm_answer)
                res = dict(
                    task_id=task_id,
                    completion=completion,
                    passed=passed,
                )
                samples += [res]
                results[task_id].append((completion_id, res))          
            pbar.update(syncode.num_samples)

        write_jsonl(syncode.out_path, samples)
        pass_at_k = compute_pass_at_k(results)

        # Log result and time
        avg_time = (time.time() - time1) / len(problems)
        syncode.logger.log_time(f"Averge time taken for each task: {avg_time:.2f}s")
        syncode.logger.log(f"Result: {pass_at_k}")
        print(f"Result: {pass_at_k}")
        syncode.logger.close()
        return samples

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
        predict_file = common.RESULTS_DIR + f"sql_pred_{syncode.mode}.txt"

        if syncode.grammar_decoder is not None:
            syncode.grammar_decoder.chat_mode = True # Do not parse input+output

        with open(predict_file, 'w') as f:
            for task_id, problem in enumerate(problems):
                if syncode.grammar_decoder is not None:
                    syncode.grammar_decoder.reset()
                results[task_id] = []
                batch_completions = syncode.model.generate_batch_completion_grammar(
                    problem['prompt'],
                    syncode.num_samples
                    )
                raw_completion = batch_completions[0]
                completion = syncode.dataset.post_process_answer(raw_completion)
                f.write(completion + '\n')
                pbar.update(syncode.num_samples)
        pbar.close()
        write_jsonl(syncode.out_path, samples)

        # Run evaluation script
        from syncode.utils.sql_spider_eval.evaluation import evaluate
        gold_file = "syncode/utils/sql_spider_eval/evaluation_examples/gold_example.txt"
        tables = "syncode/utils/sql_spider_eval/evaluation_examples/examples/tables.json"
        databses = "syncode/utils/sql_spider_eval/databases"
        scores, entries = evaluate(predict_file, gold_file, databses, etype="all", table=tables)
        print(f"Scores: {scores}")

if __name__ == "__main__":
    fire.Fire(compile_and_run)
