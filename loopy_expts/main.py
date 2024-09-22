import os
import json
import sys
from datetime import datetime
from typing import Tuple
from syncode import Syncode
from utils import Logger

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

def init(model: str, grammar: str):
    syncode = Syncode(model = model, mode='grammar_mask', grammar=grammar, parse_output_only=True, log_level=2)
    return syncode

def main(
        llm: Syncode,
        datasets_file: str,
        prompt: Tuple[str, str],
        num_samples: int = 1,
):
    Logger.log_info(f"Reading benchmarks file from {datasets_file}")
    benchmarks_file = open(datasets_file, 'r')
    benchmarks = benchmarks_file.read().split('\n')
    benchmarks_file.close()
    Logger.log_info(f"Read {len(benchmarks)} benchmarks")
    prompt_system_file, prompt_text_file = open(prompt[0], 'r'), open(prompt[1], 'r')
    prompt_system = prompt_system_file.read()
    prompt_text = prompt_text_file.read()
    prompt_system_file.close(), prompt_text_file.close()

    expt_logs = []

    for benchmark in benchmarks:
        try:
            Logger.log_info(f"Running benchmark {benchmark}")
            benchmark_code = open(benchmark, 'r').read()
            prompt = prompt_system + '\n' + prompt_text.format(code = benchmark_code)
            results = []
            for i in range(num_samples):
                Logger.log_info(f"Generating sample {i}")
                result = llm.infer(prompt)
                results.append(result)
            
            expt_logs.append({
                'file': benchmark,
                'prompt': prompt,
                'completions': results
            })
        except Exception as e:
            Logger.log_error(f'Error in benchmark {benchmark} sample {i}: {e}')
            results.append('Error in benchmark {benchmark} sample {i}: {e}')
            expt_logs.append({
                'file': benchmark,
                'error': str(e),
            })
    return expt_logs

if __name__ == '__main__':
    model = '/data/share/models/hugging_face/models--Qwen--Qwen2.5-Coder-7B/snapshots/4c1c1611f30619a8695cf6d44b492a25c52b6f00/'
    grammar = 'invariants.lark'
    Logger.log_info(f"Initializing model {model}")
    Logger.log_info(f"Initializing grammar {grammar}")
    llm = init(model, grammar)
    datasets_file = 'benchmarks.txt'
    prompt = ('templates/system_text.txt', 'templates/prompt_text.txt')
    num_samples = 10

    expt_logs = main(llm, datasets_file, prompt, num_samples)
    log_file_name = datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '_expt_logs.json'
    with open(log_file_name, 'w') as log_file:
        json.dump(expt_logs, log_file)

    print(f'Logs saved to {log_file_name}')
