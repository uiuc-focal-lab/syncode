import os
import pickle
import transformers
from grammars.python_parser import PythonIncrementalParser
from grammars.go_parser import GoIncrementalParser
from terminals_nfa import TerminalsNFA
import time
import json
import sys

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
    for i in range(len(vocab)):
        t = vocab[i]
        if 2*len(t) != len(tokenizer.decode([i, i], add_special_tokens=False)):
            vocab[i] = ' ' + t
        if t == '':
            vocab[i] = ' '
    
    return vocab

def load_nfa(language: str, tokenizer, inc_parser=None, use_cache=True):
    '''
    Loads the NFA for the given language and tokenizer. If the NFA is not cached, it is created and cached. 
    '''
    tokenizer_name = type(tokenizer).__name__
    nfa_dir = 'results/' + tokenizer_name + '/'
    nfa_path = nfa_dir + language + '_nfa.pkl'
    nfa_time = nfa_dir + language + '_time.json'
    os.makedirs(nfa_dir, exist_ok=True)
    start_time = time.time()
    if use_cache and os.path.exists(nfa_path):
        nfa = pickle.load(open(nfa_path, 'rb'))
    else:
        vocab = get_vocab_from_tokenizer(tokenizer)
        print('Time taken for loading vocab:', time.time() - start_time, flush=True)

        if inc_parser is None:
            inc_parser = create_parser(language)
            print('Time taken for loading parser:', time.time() - start_time, flush=True)

        exceptions = {}
        if language == 'python':
            exceptions = {'COMMENT': '#.*|\'\'\'.*?\'\'\'|""".*?"""/is', '_NL': '(\r?\n[\t ]*)+', 'LONG_STRING': '\'\'\'.*?\'\'\'|""".*?"""/is', 'STRING': '[ubf]?r?(".*?"|\'.*?\')'}
        nfa = TerminalsNFA(inc_parser.parser.terminals, vocab, exceptions=exceptions, special_token_ids=[tokenizer.eos_token_id])
        print(f'Time taken for creating NFA:', time.time() - start_time, flush=True)
        NFA_time = time.time() - start_time
        pickle.dump(nfa, open(nfa_path, 'wb'))
        sort_nfa = time.time() - start_time

        time_dict = {
            "Time taken for creating NFA " : NFA_time,
            "Time taken for storing the NFA " : sort_nfa,
            "The total memory of the lookup table is" : sys.getsizeof(nfa)
        }

        json_object = json.dumps(time_dict, indent=4)
        with open(nfa_time, "w") as outfile:
            outfile.write(json_object)
        print(f'Time taken for storing the NFA', time.time() - start_time, flush=True)
    return nfa

def create_parser(language):
        if language == 'python':
            return PythonIncrementalParser()
        elif language == 'go':
            return GoIncrementalParser()
        else:
            raise ValueError(f'Unknown language: {language}')

class Logger:
    # is_logging_enabled = True  # Class variable to control logging

    def __init__(self, filename, do_logger):
        self.filename = filename
        self.file = open(filename, 'w')
        self.do_logger = do_logger

    # @classmethod
    # def set_logging_enabled(cls, enabled: bool):
    #     cls.is_logging_enabled = enabled

    def log(self, msg):
        # if Logger.is_logging_enabled == True:
        if self.do_logger == True:
            self.file.write(msg + '\n')
            self.file.flush()

    def log_code(self, msg, code):
        # if Logger.is_logging_enabled == True:
        if self.do_logger == True:
            self.file.write(msg + ':\n')
            self.file.write('-'*80 + '\n')
            self.file.write(code + '\n')
            self.file.write('-'*80 + '\n')
            self.file.flush()

    def close(self):
        if self.file:
            self.file.close()



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
    
