import os
import pickle
import re
import transformers
from python_parser import PythonIncrementalParser
from terminals_nfa import TerminalsNFA
from transformers import LlamaTokenizer
import time

def get_vocab_from_tokenizer(tokenizer):
    # self.vocab is a list of readable token strings (e.g., ' hello' and '\n')
    # sorted by their token IDs (so self.vocab[0] is the first token, etc).
    vocab = [v for k, v in
                    sorted([(t_id, tokenizer.decode([t_id]))
                            for _, t_id in tokenizer.get_vocab().items()])]

    # HACK: Is there a better way to know if a token has a prefix space?
    # We should only need this for LlamaTokenizer.
    if isinstance(tokenizer, transformers.LlamaTokenizer):
        for i in range(len(vocab)):
            t = vocab[i]
            if 2*len(t) != len(tokenizer.decode([i, i], add_special_tokens=False)):
                vocab[i] = ' ' + t
            if t == '':
                vocab[i] = ' '
    
    return vocab

def load_nfa(tokenizer=None, inc_parser=None, use_cache=True):
    NFA_LOC = 'results/nfa.pkl'
    start_time = time.time()
    if use_cache and os.path.exists(NFA_LOC):
        nfa = pickle.load(open(NFA_LOC, 'rb'))
    else:
        if tokenizer is None:
            tokenizer = LlamaTokenizer.from_pretrained("/share/models/llama_model/hf/7B")
        vocab = get_vocab_from_tokenizer(tokenizer)
        print('Time taken for loading vocab:', time.time() - start_time, flush=True)

        if inc_parser is None:
            inc_parser = PythonIncrementalParser()
            print('Time taken for loading parser:', time.time() - start_time, flush=True)

        exceptions = {'COMMENT': '#.*|\'\'\'.*?\'\'\'|""".*?"""/is', '_NL': '(\r?\n[\t ]*)+', 'LONG_STRING': '\'\'\'.*?\'\'\'|""".*?"""/is', 'STRING': '[ubf]?r?(".*?"|\'.*?\')'}
        # , '_TAB': '\t+'
        nfa = TerminalsNFA(inc_parser.parser.terminals, vocab, exceptions=exceptions, special_token_ids=[tokenizer.eos_token_id])
        print(f'Time taken for creating NFA:', time.time() - start_time, flush=True)

        pickle.dump(nfa, open(NFA_LOC, 'wb'))
        print(f'Time taken for storing the NFA', time.time() - start_time, flush=True)
    return nfa

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
    