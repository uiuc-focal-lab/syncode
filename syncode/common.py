import os
from transformers import (
    LlamaTokenizer,
    LlamaForCausalLM,
    AutoTokenizer,
    AutoModelForCausalLM,
)
import torch
from llama_cpp import Llama
import numpy as np
from typing import List, Union

# Remove this in future and add instruction to set the HF_CACHE env variable
RESULTS_DIR = os.environ['RESULTS_DIR'] if 'RESULTS_DIR' in os.environ else 'results/'
HF_CACHE = os.environ['HF_CACHE'] if 'HF_CACHE' in os.environ else 'cache/'
SYNCODE_CACHE = os.environ['SYNCODE_CACHE'] if 'SYNCODE_CACHE' in os.environ else 'cache/'
HF_ACCESS_TOKEN = os.environ['HF_ACCESS_TOKEN'] if 'HF_ACCESS_TOKEN' in os.environ else None

def get_vocab_from_tokenizer(tokenizer):
    # self.vocab is a list of readable token strings (e.g., ' hello' and '\n')
    # sorted by their token IDs (so self.vocab[0] is the first token, etc).
    if isinstance(tokenizer, LlamaTokenizerWrapper):
        return tokenizer.get_vocab()
    vocab = [v for k, v in
                    sorted([(t_id, tokenizer.decode([t_id]))
                            for _, t_id in tokenizer.get_vocab().items()])]

    # HACK: Is there a better way to know if a token has a prefix space?
    if 'Llama' in tokenizer.__class__.__name__:
        for i in range(len(vocab)):
            t = vocab[i]
            if 2*len(t) != len(tokenizer.decode([i, i], add_special_tokens=False)):
                vocab[i] = ' ' + t
            if t == '':
                vocab[i] = ' '
    
    return vocab

def load_model(model_name, device, quantize):
        if model_name == 'test':
            model = AutoModelForCausalLM.from_pretrained('bigcode/tiny_starcoder_py').to(device)
        elif model_name == 'test-instruct':
            model = AutoModelForCausalLM.from_pretrained("rahuldshetty/tiny-starcoder-instruct")
        else:
            if (quantize):
                model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16, cache_dir=HF_CACHE, token=HF_ACCESS_TOKEN, trust_remote_code=True).eval().to(device)
            else:
                model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir=HF_CACHE, token=HF_ACCESS_TOKEN, trust_remote_code=True).eval().to(device)
        return model

def load_tokenizer(model_name):
        if model_name == 'test':
            tokenizer = AutoTokenizer.from_pretrained('bigcode/tiny_starcoder_py')
        elif model_name == 'test-instruct':
            tokenizer = AutoTokenizer.from_pretrained("rahuldshetty/tiny-starcoder-instruct")
        else:
            tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=HF_CACHE, token=HF_ACCESS_TOKEN, trust_remote_code=True)
        return tokenizer

class Logger:
    """
    Logger class for logging the output of the model
    """
    def __init__(self, num_samples_per_task, mode, parser, out_dir, task_id=None, log_level=1):
        self.log_level = log_level
        self.is_closed = False
        if task_id is not None:
            prefix = f"task_{task_id}_mode_{mode}_samples_{num_samples_per_task}_parser_{parser}_eval.log"
            log_file = out_dir + 'logs/tasks/' + prefix
            log_time_file = out_dir + 'logs/tasks/' + 'time_' + prefix
            log_eval_file = out_dir + 'logs/tasks/' + 'eval_' + prefix
            os.makedirs(out_dir + 'logs/tasks/', exist_ok=True)
        else:
            prefix = f"mode_{mode}_samples_{num_samples_per_task}_parser_{parser}_eval.log"
            log_file = out_dir + 'logs/' + prefix
            log_time_file = out_dir + 'logs/' + 'time_' + prefix
            log_eval_file = out_dir + 'logs/' + 'eval_' + prefix
            os.makedirs(out_dir + 'logs/', exist_ok=True)
        
        if self.log_level >= 1:
            self.log_file = log_file
            self.file = open(log_file, 'w')
            self.log_time_file = log_time_file
            self.time_file = open(log_time_file, 'w')
        self.log_eval_file = log_eval_file
        self.eval_file = open(log_eval_file, 'w')

    def log(self, msg):
        if self.log_level >= 1:
            self.file.write(msg + '\n')
            self.file.flush()
    
    def log_check(self, msg):
        if self.log_level >= 1:
            # Log warning in yellow color
            self.file.write(f"\n\n[Check]\n{msg}\n")
            self.file.flush()

    def log_error(self, msg):
        if self.log_level >= 1:
            # Log error in red color
            self.file.write(f"\n\n[ERROR]\n{msg}\n")
            self.file.flush()

    def log_time(self, msg):
        if self.log_level >= 2:
            self.time_file.write(msg + '\n')
            self.time_file.flush()
    
    def log_eval(self, msg):
        if self.log_level >= 0:
            self.eval_file.write(msg + '\n')
            self.eval_file.flush()

    def log_code(self, msg, code):
        if self.log_level >= 1:
            self.file.write(msg + ':\n')
            self.file.write('-'*80 + '\n')
            self.file.write(code + '\n')
            self.file.write('-'*80 + '\n')
            self.file.flush()

    def close(self):
        if self.log_level >= 1:
            self.file.close()
            self.time_file.close()
        self.eval_file.close()
        self.is_closed = True
    
    def open(self):
        if self.log_level >= 1:
            self.file = open(self.log_file, 'w')
            self.time_file = open(self.log_time_file, 'w')
        self.eval_file = open(self.log_eval_file, 'w')

class EmptyLogger(Logger):
    """
    A logger that does not write to file. Used while running tests.
    """
    def __init__(self):
        pass
    def log(self, msg):
        pass  
    def log_time(self, msg):
        pass   
    def log_code(self, msg, code):
        pass
    def log_eval(self, msg):
        pass
    def log_check(self, msg):
        pass
    def log_error(self, msg):
        pass
    def close(self):
        pass


class LlamaTokenizerWrapper:
    """
    This class is a minimal wrapper around LlamaTokenizer for using SynCode with llama-cpp-python LogitsProcessor. 
    """
    def __init__(self, llm: Llama):
        self.tokenizer = llm.tokenizer_
        self.vocab_size = llm.n_vocab()
        self.eos_token_id = llm.token_eos()
    
    def encode(self, text: str, add_special_tokens = True, add_bos = True, **kwargs) -> List[int]:
        return [self.tokenizer.encode(text, add_bos=True, special=True)]
    
    def decode(self, token_ids: Union[int, List[int], torch.Tensor, np.ndarray], **kwargs) -> str:
        if isinstance(token_ids, int) or (isinstance(token_ids, torch.Tensor) and token_ids.ndim == 0):
            _token_ids = [token_ids]
        elif isinstance(token_ids, (torch.Tensor, np.ndarray)):
            _token_ids = token_ids.tolist()
        else:
            _token_ids = token_ids
        return self.tokenizer.decode(_token_ids)
    
    def batch_decode(self, sequences: Union[List[int], List[List[int]], torch.Tensor, np.ndarray], **kwargs) -> List[str]:
        _sequences = [sequences] if (isinstance(sequences,list) and isinstance(sequences[0], int)) else sequences
        return [self.decode(seq) for seq in _sequences]
    
    def get_vocab(self) -> List[str]:
        return [self.decode(token_id) for token_id in range(self.vocab_size)]