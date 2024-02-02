import common
import fire
from language_model import HuggingFaceModel
from transformers import LogitsProcessorList
import os
from grammar_decoder import GrammarDecoder
from typing import Optional, Literal
from mxeval.data import write_jsonl, read_problems, get_data, get_examples
from tqdm import tqdm


class Infer:
    """Infer class for running inference on a model
    Args:
        mode (str, optional): Mode for inference. Defaults to "original".
        model (str): Model id for huggingface model hub or model name if stored locally.
        quantize (bool, optional): Quantize model. Defaults to True.
        gpu (int, optional): GPU number. Defaults to 1.
        num_samples (int, optional): Number of samples. Defaults to 1.
        grammar (str, optional): Language. Defaults to "input". "input" is used for user input. 
            other options currently supported are "python", "go", "calc"
        dataset (str, optional): Dataset. Defaults to "multi-humaneval".
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
        dataset: Literal["mbxp", "multi-humaneval", "mathqa-x", "input"] = "input",
        few_shot: bool = False,
        num_examples: int = -1,
        parse_prompt: bool = True,
        dev_mode: bool = False,
        log_level: int = 1,
        new_mask_store: bool = False,
        parser: Literal["lr", "lalr"] = "lalr",
        task_id: Optional[int] = None
    ):  
        # Check inputs
        assert mode in ["original", "grammar_mask"]
        assert dataset in ["mbxp", "multi-humaneval", "mathqa-x", "input"]
    
        # Set attributes
        self.mode = mode
        self.model_name = model
        self.quantize = quantize
        self.gpu = gpu
        self.num_samples = num_samples
        self.grammar = grammar
        self.dataset = dataset
        self.new_mask_store = new_mask_store
        self.few_shot = few_shot
        self.num_examples = num_examples
        num_samples_per_task = self.num_samples

        # Load model
        device = f"cuda:{self.gpu}"
        model = common.load_model(self.model_name, device)
        tokenizer = common.load_tokenizer(self.model_name)
        
        # Setup output directory
        out_dir = f"results/{self.model_name}/{self.grammar}/{self.dataset}/"
        out_path = out_dir + 'samples_' + str(num_samples_per_task) + '_mode_' + str(self.mode) + "_eval.jsonl"
        os.makedirs(out_dir, exist_ok=True)
        self.logger = common.Logger(num_samples_per_task, mode, out_dir, log_level=log_level)
        
        # Initialize logit processors
        logit_processors = None
        if self.mode == 'grammar_mask':
            grammar_decoder = GrammarDecoder(
                self.grammar, 
                tokenizer=tokenizer, 
                logger=self.logger, 
                use_cache=(not self.new_mask_store), 
                parse_prompt=parse_prompt,
                num_samples=num_samples_per_task, 
                dev_mode=dev_mode,
                parser=parser
                )
            logit_processors = LogitsProcessorList([grammar_decoder])

        hf_model = HuggingFaceModel(
            model, 
            self.logger, 
            tokenizer=tokenizer, 
            device=device, 
            logit_processors=logit_processors, 
            mode=self.mode, 
            max_new_tokens=200,
            grammar=self.grammar,
            )

        if self.dataset != "input": 
            self.run_code_eval(
                hf_model,
                num_samples_per_task,
                out_path,
                format_tabs=True,
                grammar_decoder=grammar_decoder,
                debug_task_id=task_id
                )
        else:
            self.user_input(hf_model, grammar_decoder)

        if self.mode == 'grammar_mask':
            self.logger.log('Non matching token count: ' + str(grammar_decoder.non_matching_token_cnt))
        
        self.logger.close()

    
    

    def run_code_eval(self, 
        hf_model,
        num_samples_per_task: int,
        out_path: str,
        format_tabs: bool = False,
        grammar_decoder: Optional[GrammarDecoder] = None,
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
            for task_id in problems:
                self.run_eval_for_task(hf_model, num_samples_per_task, format_tabs, grammar_decoder, problems, samples, pbar, task_id)
            write_jsonl(out_path, samples)
        
        else: # Debugging a specific task
            debug_task_id = list(problems.keys())[debug_task_id]
            self.run_eval_for_task(hf_model, num_samples_per_task, format_tabs, grammar_decoder, problems, samples, pbar, debug_task_id)


    def run_eval_for_task(self, hf_model, num_samples_per_task, format_tabs, grammar_decoder, problems, samples, pbar, task_id):
        """
        run evaluation for a specific task
        """
        self.logger.log(f"Running eval for task {task_id}")
        if grammar_decoder is not None:
            grammar_decoder.reset()

        if format_tabs:
            prompt = problems[task_id]["prompt"].replace("    ", "\t")
        else:
            prompt = problems[task_id]["prompt"]

        batch_completions = hf_model.generate_batch_completion(prompt, num_samples_per_task)

        for _, completion in enumerate(batch_completions):
            result = dict(
                    task_id=task_id,
                    language=problems[task_id]["language"],
                    completion=completion
                )
            samples += [result]
            
        pbar.update(num_samples_per_task)
    

    def user_input(self, hf_model, grammar_decoder):
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
            batch_completions = hf_model.generate_batch_completion(prompt, 1)
            for i, completion in enumerate(batch_completions):
                print(completion)
            if self.mode == 'grammar_mask':
                logger.log('Non matching token count: ' + str(grammar_decoder.non_matching_token_cnt))

if __name__ == "__main__":
    fire.Fire(Infer)
