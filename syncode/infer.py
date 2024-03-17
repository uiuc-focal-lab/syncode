import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import fire
import syncode.common as common
from syncode.language_model import HuggingFaceModel
from transformers import LogitsProcessorList
from syncode.grammar_decoder import GrammarDecoder
from typing import Optional, Literal
from syncode.parsers.grammars import Grammar
from syncode.dataset import Dataset
from syncode.evaluation.code_eval import CodeEval
from syncode.evaluation.math_eval import MathEval
from syncode.evaluation.sql_eval import SQLEval


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
        parse_output_only: bool = False,
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
        if self.chat_mode:
            self.parse_output_only = True
        else:
            self.parse_output_only = parse_output_only

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
                parse_output_only=self.parse_output_only,
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

if __name__ == "__main__":
    fire.Fire(compile_and_run)
