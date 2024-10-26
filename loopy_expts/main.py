import os
import json
import sys
from copy import deepcopy
from datetime import datetime
from typing import Tuple
from syncode import Syncode
from utils import Logger

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

def init(model: str, grammar: str):
    syncode = Syncode(model = model, mode='grammar_mask', grammar=grammar, parse_output_only=True, log_level=2, max_new_tokens=1000, device='cuda:0', dev_mode=True)
    return syncode

def main(
        llm: Syncode,
        datasets_file: str,
        prompt: Tuple[str, str],
        num_samples: int = 1,
):
    Logger.debug = True
    try:
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

        for i, benchmark in enumerate(benchmarks):
            try:
                Logger.log_info(f"[{i + 1}/{len(benchmarks)}] Processing benchmark {benchmark}")
                benchmark_code = open(benchmark, 'r').read()
                prompt_text_template = deepcopy(prompt_text)
                prompt = prompt_system + '\n' + prompt_text_template.format(code = benchmark_code)
                benchmark_log = {
                    'file': benchmark,
                    'prompt': prompt,
                    'completions': []
                }
                Logger.log_model_request(llm.model_name, [{'role': 'Prompt', 'content': prompt}])
                for i in range(num_samples):
                    Logger.log_info(f"Generating sample {i + 1}/{num_samples}")
                    result = llm.infer(prompt)
                    Logger.log_model_response(llm.model_name, [result])
                    benchmark_log['completions'].append(result)
                
                expt_logs.append(benchmark_log)
            except Exception as e:
                Logger.log_error(f'Error in benchmark {benchmark} sample {i}: {e}')
                benchmark_log['error'] = str(e)
                expt_logs.append(benchmark_log)
    except KeyboardInterrupt:
        Logger.log_info('Received keyboard interrupt. Exiting...')
    
    return expt_logs

if __name__ == '__main__':
    model = 'Qwen/Qwen2.5-Coder-7B'
    grammar = 'invariants.lark'
    Logger.log_info(f"Initializing model {model}")
    Logger.log_info(f"Initializing grammar {grammar}")
    llm = init(model, grammar)
    datasets_file = 'benchmarks.txt'
    prompt = ('templates/system_text.txt', 'templates/prompt_text.txt')
    num_samples = 2

    expt_logs = main(llm, datasets_file, prompt, num_samples)
    log_file_name = datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '_expt_logs.json'
    with open(log_file_name, 'w') as log_file:
        json.dump(expt_logs, log_file, indent=4)

    print(f'Logs saved to {log_file_name}')
