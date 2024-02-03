import os
from transformers import (
    LlamaTokenizer,
    LlamaForCausalLM,
    AutoTokenizer,
    AutoModelForCausalLM,
    LogitsProcessorList
)
import torch

# Remove this in future and add instruction to set the HF_CACHE env variable
HF_CACHE = '/share/models/hugging_face/'
# HF_CACHE = os.environ['HF_CACHE']
HF_ACCESS_TOKEN = os.environ['HF_ACCESS_TOKEN'] if 'HF_ACCESS_TOKEN' in os.environ else None

def get_vocab_from_tokenizer(tokenizer):
    # self.vocab is a list of readable token strings (e.g., ' hello' and '\n')
    # sorted by their token IDs (so self.vocab[0] is the first token, etc).
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

def load_model(model_name, device):
        llama_models = ["Llama-7b", "Llama-13b", "CodeLlama-7b", "CodeLlama-7b-Python"]
        if model_name not in llama_models:
            model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16, cache_dir=HF_CACHE, token=HF_ACCESS_TOKEN, trust_remote_code=True).eval().to(device)
        elif model_name in llama_models:
            model_location = "/share/models/hugging_face/" + model_name
            model = LlamaForCausalLM.from_pretrained(model_location, torch_dtype=torch.bfloat16).eval().to(device)
        return model

def load_tokenizer(model_name):
        llama_models = ["Llama-7b", "Llama-13b", "CodeLlama-7b", "CodeLlama-7b-Python"]
        if model_name not in llama_models:
            tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=HF_CACHE, token=HF_ACCESS_TOKEN, trust_remote_code=True)
        elif model_name in llama_models:
            model_location = "/share/models/hugging_face/" + model_name
            tokenizer = LlamaTokenizer.from_pretrained(model_location)
        return tokenizer

class Logger:
    """
    Logger class for logging the output of the model
    """
    def __init__(self, num_samples_per_task, mode, out_dir, log_level=1):
        self.log_level = log_level
        prefix = 'samples_' + str(num_samples_per_task) + '_mode_' + str(mode) + "_eval.log"
        log_file = out_dir + 'logs/' + prefix
        log_time_file = out_dir + 'logs/' + 'time_' + prefix
        log_eval_file = out_dir + 'logs/' + 'eval_' + prefix
        os.makedirs(out_dir + 'logs/', exist_ok=True)

        self.log_file = log_file
        self.file = open(log_file, 'w')
        self.log_time_file = log_time_file
        self.time_file = open(log_time_file, 'w')

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
            self.file.write(msg + '\n')
            self.file.flush()

    def log_code(self, msg, code):
        if self.log_level >= 1:
            self.file.write(msg + ':\n')
            self.file.write('-'*80 + '\n')
            self.file.write(code + '\n')
            self.file.write('-'*80 + '\n')
            self.file.flush()

    def close(self):
        self.file.close()

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


def run_tests(tests):
    test_result = {}

    for test in tests:
        print(f"Running test {test.__name__}")
        # try:
        test()
        print(f"Test {test.__name__} passed.")
        test_result[test.__name__] = 'passed'
        # except AssertionError:
        #     _, _, tb = sys.exc_info()
        #     traceback.print_tb(tb) # Fixed format
        #     tb_info = traceback.extract_tb(tb)
        #     filename, line, func, text = tb_info[-1]
        #     print('An error occurred on line {} in statement {}'.format(line, text))
        #     test_result[test.__name__] = 'failed'
        # except Exception as e:
        #     print(f"Test {test.__name__} failed.")
        #     print(e)
        #     test_result[test.__name__] = 'failed'
        
        print("-"*80)

    tests_passed = 0
    for test_name, result in test_result.items():
        if result == 'passed':
            tests_passed += 1
            # Use green color for passed tests
            print(f"\033[92m{test_name}: {result}\033[0m")
        else:
            # Use red color for failed tests
            print(f"\033[91m{test_name}: {result}\033[0m")
    print(f"Passed {tests_passed}/{len(tests)} tests.")
    