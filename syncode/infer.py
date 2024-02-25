import time, os
import fire
import syncode.common as common
from syncode.language_model import HuggingFaceModel
from transformers import LogitsProcessorList
from syncode.grammar_decoder import GrammarDecoder
from typing import Optional, Literal
from mxeval.data import write_jsonl, get_data, get_examples
from tqdm import tqdm
from syncode.evaluation import check_coorectness
from syncode.parsers.grammars import Grammar

def compile_and_run(model, mode="original", quantize=True, device="cuda", num_samples=1, grammar="python", dataset="input", few_shot=False, num_examples=-1, parse_prompt=True, dev_mode=False, log_level=1, new_mask_store=False, parser="lalr", task_id=None, **kwargs):
    sc = Syncode(model, mode=mode, quantize=quantize, device=device, num_samples=num_samples, grammar=grammar, dataset=dataset, few_shot=few_shot, num_fs_examples=num_examples, chat_mode=parse_prompt, dev_mode=dev_mode, log_level=log_level, new_mask_store=new_mask_store, parser=parser, task_id=task_id, **kwargs)
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
        few_shot (bool, optional): Run few shoting prompting. Defaults to False.
        num_fs_examples (int, optional): Number of examples for few shot prompting. Defaults to -1.
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
        grammar: str = "python",
        dataset: Literal["mbxp", "humaneval", "mathqa-x", "input"] = "input",
        few_shot: bool = False,
        num_fs_examples: int = -1,
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
        assert dataset in ["mbxp", "humaneval", "mathqa-x", "input"]
        gen_kwargs = {'max_length', 'max_new_tokens', 'min_length', 'min_new_tokens', 'early_stopping', 'do_sample', 'num_beams', 'use_cache', 'temperature', 'top_k', 'top_p', 'num_return_sequences', 'pad_token_id', 'eos_token_id'}
        invalid_kwargs = kwargs.keys() - gen_kwargs
        assert invalid_kwargs == set(), f"Invalid arguments {invalid_kwargs}"

        # Set attributes
        self.mode = mode
        self.model_name = model
        self.quantize = quantize
        self.device = device
        self.num_samples = num_samples
        self.grammar = Grammar(grammar)
        self.new_mask_store = new_mask_store
        self.few_shot = few_shot
        self.num_fs_examples = num_fs_examples
        dataset_dirmap = {"mbxp": "mbxp", "humaneval": "multi-humaneval", "mathqa-x": "mathqa-x"}
        self.dataset = dataset_dirmap[dataset] if dataset != "input" else "input"
        self.parser = parser
        self.chat_mode = chat_mode

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

        kwargs['max_new_tokens'] = kwargs.get('max_new_tokens', 200)
        kwargs['do_sample'] = kwargs.get('do_sample', False)
        kwargs['use_cache'] = kwargs.get('use_cache', True)
        kwargs['temperature'] = kwargs.get('temperature', 0.2)
        kwargs['top_p'] = kwargs.get('top_p', 0.95)
        kwargs['eos_token_id'] = kwargs.get('eos_token_id', tokenizer.eos_token_id)
        kwargs['pad_token_id'] = kwargs.get('pad_token_id', tokenizer.eos_token_id) # model has no pad token

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

    def infer(self, prompt = None, task_id=None):
        if self.logger.is_closed:
            self.logger.open()

        if self.dataset != "input": 
            output = self.run_code_eval(
                self.num_samples,
                self.out_path,
                format_tabs=True,
                debug_task_id=task_id
                )
        else:
            return self.user_input(prompt)
        self.logger.close()
        return output

    def get_output_path(self):
        out_dir = f"results/{self.model_name}/{self.grammar}/{self.dataset}/"
        out_path = out_dir + 'samples_' + str(self.num_samples) + '_mode_' + str(self.mode) + "_eval.jsonl"
        os.makedirs(out_dir, exist_ok=True)
        return out_dir,out_path

    def run_code_eval(self, 
        num_samples_per_task: int,
        out_path: str,
        format_tabs: bool = False,
        debug_task_id: Optional[int] = None
        ):
        """
        Run evaluation on the model
        """
        if self.few_shot:
            problems = {problem['task_id'] : problem for problem in get_examples(self.dataset, self.grammar.name, self.num_fs_examples)}
        else:
            problems = get_data(self.dataset, self.grammar.name)

        samples = []
        outputs = []
        pbar = tqdm(total=len(problems) * num_samples_per_task)
        if debug_task_id is None:
            time1 = time.time()
            for task_id in problems:
                outputs.append(self.run_eval_for_task(num_samples_per_task, format_tabs, problems, samples, pbar, task_id))
            write_jsonl(out_path, samples)
            avg_time = (time.time() - time1) / len(problems)
            self.logger.log_time(f"Averge time taken for each task: {avg_time:.2f}s")
            functional_result = check_coorectness(out_path, logger=self.logger)
            self.logger.log(f"Functional result: {functional_result}")

            # Also log these results in a separate file
            self.write_results(out_path, avg_time, functional_result)
        else: # Debugging a specific task
            debug_task_id = list(problems.keys())[debug_task_id]
            return self.run_eval_for_task(num_samples_per_task, format_tabs, problems, samples, pbar, debug_task_id)
        return outputs

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

    def run_eval_for_task(self, num_samples_per_task, format_tabs, problems, samples, pbar, task_id):
        """
        run evaluation for a specific task
        """
        self.logger.log(f"Running eval for task {task_id}")
        if self.grammar_decoder is not None:
            self.grammar_decoder.reset()

        if format_tabs:
            prompt = problems[task_id]["prompt"].replace("    ", "\t")
        else:
            prompt = problems[task_id]["prompt"]

        batch_completions = self.model.generate_batch_completion_grammar(prompt, num_samples_per_task)

        for _, completion in enumerate(batch_completions):
            result = dict(
                    task_id=task_id,
                    language=problems[task_id]["language"],
                    completion=completion
                )
            samples += [result]
        pbar.update(num_samples_per_task)
        return batch_completions
    

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


if __name__ == "__main__":
    fire.Fire(compile_and_run)
