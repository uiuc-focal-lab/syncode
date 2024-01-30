import common
import fire
from language_model import HuggingFaceModel
from transformers import (
    LlamaTokenizer,
    LlamaForCausalLM,
    AutoTokenizer,
    AutoModelForCausalLM,
    LogitsProcessorList
)
import os
import torch
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
        language (str, optional): Language. Defaults to "python".
        dataset (str, optional): Dataset. Defaults to "multi-humaneval".
        new_nfa (bool, optional): Use new NFA. Defaults to False.
        few_shot (bool, optional): Run few shoting prompting. Defaults to False.
        num_examples (int, optional): Number of examples for few shot prompting. Defaults to -1.

        List of currently tested models:
        Llama models: "Llama-7b", "CodeLlama-7b", "CodeLlama-7b-Python", "Llama-13b"
        CodeGen models: "Salesforce/codegen-350M-multi", "Salesforce/codegen2-1b"
        Bigcode models: "bigcode/starcoderbase-1b", "bigcode/santacoder" (1.1b WIP)
        WizardLM models: "WizardLM/WizardCoder-1B-V1.0"
    """
    def __init__(
        self, 
        model: str,
        mode: Literal["original", "grammar_mask", "synchromesh"] = "original",
        quantize: bool = True,
        gpu: int = 1,
        num_samples: int = 1,
        language: Literal["python", "go"] = "python",
        dataset: Literal["mbxp", "multi-humaneval", "mathqa-x"] = "multi-humaneval",
        new_nfa: bool = False,
        few_shot: bool = False,
        num_examples: int = -1
    ):  
        # Check inputs
        assert mode in ["original", "grammar_mask", "synchromesh"]
        assert language in ["python", "go"]
        assert dataset in ["mbxp", "multi-humaneval", "mathqa-x"]
    
        # Set attributes
        self.mode = mode
        self.model = model
        self.quantize = quantize
        self.gpu = gpu
        self.num_samples = num_samples
        self.language = language
        self.dataset = dataset
        self.new_nfa = new_nfa
        self.few_shot = few_shot
        self.num_examples = num_examples
        num_samples_per_task = self.num_samples

        # Load model
        device = f"cuda:{self.gpu}"
        llama_models = ["Llama-7b", "Llama-13b", "CodeLlama-7b", "CodeLlama-7b-Python"]
        if self.model not in llama_models:
            tokenizer = AutoTokenizer.from_pretrained(self.model, cache_dir=common.HF_CACHE, token=common.HF_ACCESS_TOKEN, trust_remote_code=True)
            model = AutoModelForCausalLM.from_pretrained(self.model, torch_dtype=torch.bfloat16, cache_dir=common.HF_CACHE, token=common.HF_ACCESS_TOKEN, trust_remote_code=True).eval().to(device)
            out_dir = f"results/{self.model}/{self.language}/{self.dataset}/"
        elif self.model in llama_models:
            model_location = "/share/models/hugging_face/" + self.model
            tokenizer = LlamaTokenizer.from_pretrained(model_location)
            model = LlamaForCausalLM.from_pretrained(model_location, torch_dtype=torch.bfloat16).eval().to(device)
            out_dir = f"results/{self.model}/{self.language}/{self.dataset}/"

        # Setup output directory
        out_path = out_dir + 'samples_' + str(num_samples_per_task) + '_mode_' + str(self.mode) + "_eval.jsonl"
        os.makedirs(out_dir, exist_ok=True)
        log_file = out_dir + 'logs/' + 'samples_' + str(num_samples_per_task) + '_mode_' + str(self.mode) + "_eval.log"
        os.makedirs(out_dir + 'logs/', exist_ok=True)
        logger = common.Logger(log_file)
        
        # Initialize logit processors
        logit_processors = None
        if self.mode == 'grammar_mask':
            use_cache = not self.new_nfa
            grammar_decoder = GrammarDecoder(self.language, tokenizer=tokenizer, logger=logger, use_cache=use_cache)
            logit_processors = LogitsProcessorList([grammar_decoder])

        hf_model = HuggingFaceModel(
            model, 
            logger, 
            tokenizer=tokenizer, 
            device=device, 
            logit_processors=logit_processors, 
            mode=self.mode, 
            max_new_tokens=200,
            language=self.language,
            )

        self.run_eval(
            hf_model,
            num_samples_per_task,
            out_path,
            logger,
            format_tabs=True,
            )

        if self.mode == 'grammar_mask':
            logger.log('Non matching token count: ' + str(grammar_decoder.non_matching_token_cnt))
        
        logger.close()
    

    def run_eval(self, 
        hf_model,
        num_samples_per_task: int,
        out_path: str,
        logger: common.Logger,
        format_tabs: bool = False,
        ):
        """
        Run evaluation on the model
        """
        if self.few_shot:
            problems = {problem['task_id'] : problem for problem in get_examples(self.dataset, self.language, self.num_examples)}
        else:
            problems = get_data(self.dataset, self.language)

        samples = []
        pbar = tqdm(total=len(problems) * num_samples_per_task)

        for task_id in problems:
            if format_tabs:
                prompt = problems[task_id]["prompt"].replace("    ", "\t")
            else:
                prompt = problems[task_id]["prompt"]

            batch_completions = hf_model.generate_batch_completion(prompt, num_samples_per_task)

            for i, completion in enumerate(batch_completions):
                result = dict(
                    task_id=task_id,
                    language=problems[task_id]["language"],
                    completion=completion
                )
                samples += [result]
            
            pbar.update(num_samples_per_task)
        write_jsonl(out_path, samples)
        
if __name__ == "__main__":
    fire.Fire(Infer)
