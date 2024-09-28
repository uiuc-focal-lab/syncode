import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import fire
import syncode.common as common
from syncode.language_model import HuggingFaceModel
from syncode.grammar_decoder import SyncodeLogitsProcessor
from typing import Optional, Literal, Union
from syncode.parsers.grammars import Grammar
from syncode.dataset import Dataset
from syncode.evaluation.code_eval import CodeEval
from syncode.evaluation.math_eval import MathEval
from syncode.evaluation.sql_eval import SQLEval
from syncode.evaluation.json_eval import JSONEval
from syncode.evaluation.fol_eval import FOLEval


def compile_and_run(model, mode="grammar_strict", quantize=True, device="cuda", num_samples=1, grammar=None, dataset="input", num_few_shot=0, chat_mode=False, dev_mode=False, log_level=1, new_mask_store=False, parser="lalr", task_id=None, **kwargs):

    syncode = Syncode(model, mode=mode, quantize=quantize, device=device, num_samples=num_samples, grammar=grammar, chat_mode=chat_mode, dev_mode=dev_mode, log_level=log_level, new_mask_store=new_mask_store, parser=parser, **kwargs)
    
    if dataset == "input":
        syncode.infer()
    else:
        # Setup output directory and logger
        out_dir, out_path = common.get_output_path(model, grammar, dataset, num_samples, mode)
        logger = common.Logger(num_samples, mode, parser, out_dir, log_level=log_level, task_id=task_id)
        if syncode.grammar_decoder is not None: syncode.grammar_decoder.logger = logger

        # Run evaluation
        syncode.evaluate(dataset=dataset, task_id=task_id, out_path=out_path, logger=logger, num_few_shot=num_few_shot)


class Syncode:
    """Syncode class for running inference on a model
    Args:
        mode (str, optional): Mode for inference. Defaults to "grammar_mask". 
            "original" for original model, "grammar_mask" for grammar mask, "grammar_strict" for strict grammar mask.
        
        model (str): Model id for huggingface model hub or model name if stored locally.
        
        quantize (bool, optional): Quantize model. Defaults to True.
        
        device (str, optional): Device to use. Defaults to "cuda".
        
        num_samples (int, optional): Number of samples. Defaults to 1.
        
        grammar (str, optional): Language. Defaults to "input". "input" is used for user input. 
            other options currently supported are "python", "go", "calc"
                
        new_mask_store (bool, optional): Use new DFA mask store. Defaults to False.
                
        chat_mode (bool, optional): Parse only the (output) and not (prompt+output) in chat mode. Defaults to False.
        
        dev_mode (bool, optional): Development mode. Defaults to False.

        log_level (int, optional): Log level. Defaults to 2. 0 for no logs, 1 for minimal logs, 2 for all logs including time.
        
        parser (str, optional): Parser to use. Defaults to "lalr".
    """
    def __init__(
        self, 
        model: str,
        mode: Literal["original", "grammar_mask", "grammar_strict"] = "grammar_strict",
        quantize: bool = True,
        device: str = "cuda",
        num_samples: int = 1,
        grammar: Optional[str] = None,
        chat_mode: bool = False,
        parse_output_only: bool = False,
        dev_mode: bool = False,
        log_level: int = 1,
        new_mask_store: bool = False,
        parser: Literal["lr", "lalr"] = "lalr",
        **kwargs
    ):  
        # Check inputs
        assert mode in ["original", "grammar_mask", "grammar_strict"]
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
        self.parser = parser
        self.chat_mode = chat_mode
        self.log_level = log_level

        if self.chat_mode:
            self.parse_output_only = True
        else:
            self.parse_output_only = parse_output_only

        # Set the grammar
        self.language = grammar
        self.grammar = Grammar(grammar) if self.is_grammar_mode() else None

        # Load model
        model = common.load_model(self.model_name, device, quantize)
        tokenizer = common.load_tokenizer(self.model_name)
        
        # Initialize logit processors
        self.grammar_decoder = None
        
        if self.is_grammar_mode():
            self.grammar_decoder = SyncodeLogitsProcessor(
                self.grammar, 
                tokenizer=tokenizer, 
                use_cache=(not self.new_mask_store), 
                parse_output_only=self.parse_output_only,
                num_samples=self.num_samples, 
                dev_mode=dev_mode,
                parser=parser,
                mode=mode,
                )

        # Set LLM max new tokens to 200 by default
        kwargs['max_new_tokens'] = kwargs.get('max_new_tokens', 200)

        self.model = HuggingFaceModel(
            model, 
            grammar=self.grammar,
            tokenizer=tokenizer, 
            device=device, 
            grammar_decoder=self.grammar_decoder, 
            mode=self.mode, 
            **kwargs
            )

    def is_grammar_mode(self):
        return self.mode == 'grammar_mask' or self.mode == 'grammar_strict'

    def infer(self, prompt: Union[str, list]=None, stop_words=[]):
        output = self.user_input(prompt, stop_words=stop_words)
        return output

    def evaluate(
            self, 
            dataset: Literal["mbxp", "humaneval", "mathqa-x", "gsm8k", "spider", "json_eval"],
            out_path: str=None,
            num_few_shot:int=0,
            logger=common.EmptyLogger(), 
            task_id=None,
            prompt_type='original' # For JSONEvalL: "original" or "explicit"
        ) -> dict:
        """
        Run evaluation on the model:

        Args:
            dataset (str): Dataset to evaluate on. Options are "mbxp", "humaneval", "mathqa-x", "gsm8k", "spider", "json_eval".
        
            num_few_shot (int, optional): Number of examples for few shot prompting. Defaults to 0.

            task_id (int, optional): For debugging a specific task. Defaults to None.
        """
        if logger.is_closed:
            logger.open()

        # Load the dataset
        self.dataset = Dataset(dataset, language=self.language, num_few_shot=num_few_shot)

        if self.dataset.type == "code": 
            output = CodeEval.run_code_eval(self, self.num_samples, out_path, format_tabs=True, debug_task_id=task_id, logger=logger)
        elif self.dataset.type == "math":
            output = MathEval.run_math_eval(self, out_path, debug_task_id=task_id, logger=logger)
        elif self.dataset.type == "sql":
            output = SQLEval.run_eval(self, out_path, debug_task_id=task_id)
        elif self.dataset.type == "fol":
            output = FOLEval.run_eval(self, out_path, debug_task_id=task_id)
        elif self.dataset.type == "json":
            output = JSONEval.run_json_eval(self, out_path, debug_task_id=task_id, logger=logger, prompt_type=prompt_type)
        else:
            raise ValueError(f"Dataset type {self.dataset.type} not supported")
        logger.close()
        return output

    def user_input(self, prompt: Union[str, list], stop_words=[]):
        """
        Run user input on the model with grammar mask
        """
        if prompt:
            # Run inference
            return self.model.generate_batch_completion_grammar(prompt, self.num_samples, stop_words=stop_words)
        else:
            while True:
                prompt = input('Enter prompt: ')
                prompt = prompt.replace('\\n', '\n').replace('\\"', '\"').replace('\\t', '\t').replace("\\'", "\'").replace('\\b', '\b').replace('\\r', '\r') if self.grammar.name == 'python' else prompt
                if prompt == "exit":
                    break

                batch_completions = self.model.generate_batch_completion_grammar(prompt, self.num_samples)
                for i, completion in enumerate(batch_completions):
                    print(prompt + completion)

if __name__ == "__main__":
    fire.Fire(compile_and_run)
