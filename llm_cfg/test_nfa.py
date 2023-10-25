import re
import time
import common
from incremental_parser import IncrementalParser
from terminals_nfa import TerminalsNFA
from transformers import LlamaTokenizer

def test_nfa():
    nfa = common.load_nfa(use_cache=True)
        
    query_start_time = time.time()
    nfa.get_overapprox_tokens_mask('1', ['PLUS']) # 0.02 seconds for mask
    print(f'Time taken for mask query:', time.time() - query_start_time, flush=True)

    query_start_time = time.time()
    nfa.get_overapprox_tokens_mask('1', ['PLUS'], get_list=True) # 10^-4 seconds for list
    print(f'Time taken for list query:', time.time() - query_start_time, flush=True)

    assert all(t in nfa.get_overapprox_tokens_mask('1', ['PLUS'], get_list=True) for t in [' +', ' +=', ' ++'])

def test_nfa2():
    nfa = common.load_nfa(use_cache=True)
    assert len(nfa.get_overapprox_tokens_mask('\n"""comment"""\n', ['NAME'], get_list=True)) > 0

tests = [test_nfa, test_nfa2]
common.run_tests(tests)