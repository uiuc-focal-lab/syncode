import os

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


class Logger:
    """
    Logger class for logging the output of the model
    """
    def __init__(self, num_samples_per_task, mode, out_dir, log_level=1):
        self.log_level = log_level
        log_file = out_dir + 'logs/' + 'samples_' + str(num_samples_per_task) + '_mode_' + str(mode) + "_eval.log"
        log_time_file = out_dir + 'logs/' + 'time_samples_' + str(num_samples_per_task) + '_mode_' + str(mode) + "_eval.log"
        os.makedirs(out_dir + 'logs/', exist_ok=True)

        self.log_file = log_file
        self.file = open(log_file, 'w')
        self.log_time_file = log_time_file
        self.time_file = open(log_time_file, 'w')

    def log(self, msg):
        if self.log_level >= 1:
            self.file.write(msg + '\n')
            self.file.flush()
    
    def log_time(self, msg):
        if self.log_level >= 2:
            self.time_file.write(msg + '\n')
            self.time_file.flush()
    
    def log_code(self, msg, code):
        if self.log_level >= 1:
            self.file.write(msg + ':\n')
            self.file.write('-'*80 + '\n')
            self.file.write(code + '\n')
            self.file.write('-'*80 + '\n')
            self.file.flush()

    def close(self):
        self.file.close()

class TestLogger(Logger):
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
    