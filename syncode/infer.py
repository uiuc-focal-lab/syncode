import time
import common
import fire
from language_model import HuggingFaceModel
from transformers import LogitsProcessorList
import os
from grammar_decoder import GrammarDecoder
from typing import Optional, Literal
from mxeval.data import write_jsonl, read_problems, get_data, get_examples
from tqdm import tqdm
from evaluation import check_coorectness

def compile_and_run(model, mode="original", quantize=True, gpu=1, num_samples=1, grammar="python", dataset="input", few_shot=False, num_examples=-1, parse_prompt=True, dev_mode=False, log_level=1, new_mask_store=False, parser="lalr", task_id=None, **kwargs):
    sc = Syncode(model, mode=mode, quantize=quantize, gpu=gpu, num_samples=num_samples, grammar=grammar, dataset=dataset, few_shot=few_shot, num_examples=num_examples, parse_prompt=parse_prompt, dev_mode=dev_mode, log_level=log_level, new_mask_store=new_mask_store, parser=parser, **kwargs)

    sc.infer(task_id=task_id)

class Syncode:
    """Syncode class for running inference on a model
    Args:
        mode (str, optional): Mode for inference. Defaults to "original".
        model (str): Model id for huggingface model hub or model name if stored locally.
        quantize (bool, optional): Quantize model. Defaults to True.
        gpu (int, optional): GPU number. Defaults to 1.
        num_samples (int, optional): Number of samples. Defaults to 1.
        grammar (str, optional): Language. Defaults to "input". "input" is used for user input. 
            other options currently supported are "python", "go", "calc"
        dataset (str, optional): Dataset. Defaults to "humaneval".
        new_mask_store (bool, optional): Use new DFA mask store. Defaults to False.
        few_shot (bool, optional): Run few shoting prompting. Defaults to False.
        num_examples (int, optional): Number of examples for few shot prompting. Defaults to -1.
        parse_prompt (bool, optional): Parse prompt. Defaults to True.
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
        gpu: int = 1,
        num_samples: int = 1,
        grammar: str = "python",
        dataset: Literal["mbxp", "humaneval", "mathqa-x", "input"] = "input",
        few_shot: bool = False,
        num_examples: int = -1,
        parse_prompt: bool = True,
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
        assert len(kwargs) == 0, f"Invalid arguments: {kwargs}"

        # Set attributes
        self.mode = mode
        self.model_name = model
        self.quantize = quantize
        self.gpu = gpu
        self.num_samples = num_samples
        self.grammar = grammar
        self.new_mask_store = new_mask_store
        self.few_shot = few_shot
        self.num_examples = num_examples
        dataset_dirmap = {"mbxp": "mbxp", "humaneval": "multi-humaneval", "mathqa-x": "mathqa-x"}
        self.dataset = dataset_dirmap[dataset]

        # Load model
        device = f"cuda:{self.gpu}"
        model = common.load_model(self.model_name, device)
        tokenizer = common.load_tokenizer(self.model_name)
        
        # Setup output directory
        out_dir, self.out_path = self.get_output_path()
        self.logger = common.Logger(self.num_samples, mode, parser, out_dir, log_level=log_level)
        
        # Initialize logit processors
        logit_processors = None
        self.grammar_decoder = None
        
        if self.mode == 'grammar_mask':
            self.grammar_decoder = GrammarDecoder(
                self.grammar, 
                tokenizer=tokenizer, 
                logger=self.logger, 
                use_cache=(not self.new_mask_store), 
                parse_prompt=parse_prompt,
                num_samples=self.num_samples, 
                dev_mode=dev_mode,
                parser=parser
                )
            logit_processors = LogitsProcessorList([self.grammar_decoder])

        self.model = HuggingFaceModel(
            model, 
            self.logger, 
            tokenizer=tokenizer, 
            device=device, 
            logit_processors=logit_processors, 
            mode=self.mode, 
            max_new_tokens=200,
            grammar=self.grammar,
            )

    def infer(self, task_id=None):
        if self.dataset != "input": 
            self.run_code_eval(
                self.num_samples,
                self.out_path,
                format_tabs=True,
                debug_task_id=task_id
                )
        else:
            self.user_input()
        self.logger.close()


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
            problems = {problem['task_id'] : problem for problem in get_examples(self.dataset, self.grammar, self.num_examples)}
        else:
            problems = get_data(self.dataset, self.grammar)

        samples = []
        pbar = tqdm(total=len(problems) * num_samples_per_task)

        if debug_task_id is None:
            time1 = time.time()
            for task_id in problems:
                self.run_eval_for_task(num_samples_per_task, format_tabs, problems, samples, pbar, task_id)
            write_jsonl(out_path, samples)
            self.logger.log_time(f"Averge time taken for each task: {(time.time() - time1) / (len(problems)):.2f}s")
            functional_result = check_coorectness(out_path, logger=self.logger)
            self.logger.log(f"Functional result: {functional_result}")
        else: # Debugging a specific task
            debug_task_id = list(problems.keys())[debug_task_id]
            self.run_eval_for_task(num_samples_per_task, format_tabs, problems, samples, pbar, debug_task_id)


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

        batch_completions = self.model.generate_batch_completion(prompt, num_samples_per_task)

        for _, completion in enumerate(batch_completions):
            result = dict(
                    task_id=task_id,
                    language=problems[task_id]["language"],
                    completion=completion
                )
            samples += [result]
        pbar.update(num_samples_per_task)
    

    def user_input(self):
        """
        Run user input on the model
        Args:
            hf_model (HuggingFaceModel): HuggingFaceModel object.
            logger (common.Logger): Logger object.
            grammar_decoder (GrammarDecoder): GrammarDecoder object.
        """
        while True:
            prompt = input("Enter prompt: ")
            if prompt == "exit":
                break
            batch_completions = self.model.generate_batch_completion(prompt, 1)
            for i, completion in enumerate(batch_completions):
                print(completion)

if __name__ == "__main__":
    fire.Fire(compile_and_run)
