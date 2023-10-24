import os
import pickle
import time
from common import run_tests, get_vocab_from_tokenizer
from incremental_parser import IncrementalParser
from terminals_nfa import TerminalsNFA
from transformers import LlamaTokenizer

NFA_LOC = 'results/nfa.pkl'

def test_nfa(load=False):
    start_time = time.time()

    if load and os.path.exists(NFA_LOC):
        nfa = pickle.load(open(NFA_LOC, 'rb'))
    else:
        tokenizer = LlamaTokenizer.from_pretrained("/share/models/llama_model/hf/7B")
        vocab = get_vocab_from_tokenizer(tokenizer)
        print('Time taken for loading vocab:', time.time() - start_time, flush=True)
    
        inc_parser = IncrementalParser()
        print('Time taken for loading parser:', time.time() - start_time, flush=True)

        nfa = TerminalsNFA(inc_parser.parser.terminals, vocab)
        pickle.dump(nfa, open(NFA_LOC, 'wb'))
        print(f'Time taken for creating NFA:', time.time() - start_time, flush=True)
        
    print(nfa.get_overapprox_tokens('1', ['PLUS']))
    # print(nfa.get_overapprox_tokens('1.2', ['PLUS']))
    # print(nfa.get_overapprox_tokens(' ', ['PLUS']))

    assert all(t in nfa.get_overapprox_tokens('1', ['PLUS']) for t in [' +', ' +=', ' ++'])

tests = [test_nfa]
run_tests(tests)