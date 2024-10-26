import os
import json
import sys
from copy import deepcopy
from datetime import datetime
from typing import Tuple
from syncode import Syncode
from utils import Logger

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))


def init(model: str, grammar: str):
    device = ""
    if model == "Qwen/Qwen2.5-Coder-7B":
        device = "cuda:0"
    else:
        device = "cuda:1"
    syncode = Syncode(
        model=model,
        mode="grammar_mask",
        grammar=grammar,
        parse_output_only=True,
        log_level=2,
        max_new_tokens=1000,
        device=device,
        dev_mode=True,
        temperature=0.7,
        do_sample=True,
    )
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
        benchmarks_file = open(datasets_file, "r")
        benchmarks = benchmarks_file.read().split("\n")
        benchmarks_file.close()
        Logger.log_info(f"Read {len(benchmarks)} benchmarks")
        prompt_system_file, prompt_text_file = open(prompt[0], "r"), open(
            prompt[1], "r"
        )
        prompt_system = prompt_system_file.read()
        prompt_text = prompt_text_file.read()
        prompt_system_file.close(), prompt_text_file.close()

        expt_logs = []

        for i, benchmark in enumerate(benchmarks):
            try:
                Logger.log_info(
                    f"[{i + 1}/{len(benchmarks)}] Processing benchmark {benchmark}"
                )
                benchmark_code = open(benchmark, "r").read()
                prompt_text_template = deepcopy(prompt_text)
                prompt = (
                    prompt_system
                    + "\n"
                    + prompt_text_template.format(code=benchmark_code)
                )
                benchmark_log = {"file": benchmark, "prompt": prompt, "completions": []}
                Logger.log_model_request(
                    llm.model_name, [{"role": "Prompt", "content": prompt}]
                )
                for i in range(num_samples):
                    Logger.log_info(f"Generating sample {i + 1}/{num_samples}")
                    result = llm.infer(prompt)
                    Logger.log_model_response(llm.model_name, [result])
                    benchmark_log["completions"].append(result)

                expt_logs.append(benchmark_log)
            except Exception as e:
                Logger.log_error(f"Error in benchmark {benchmark} sample {i}: {e}")
                benchmark_log["error"] = str(e)
                expt_logs.append(benchmark_log)
    except KeyboardInterrupt:
        Logger.log_info("Received keyboard interrupt. Exiting...")

    return expt_logs


if __name__ == "__main__":
    model = "meta-llama/CodeLlama-7b-Instruct-hf"
    if len(sys.argv) < 2:
        sys.argv.append("codellama")
    if sys.argv[1] == "qwencoder":
        model = "Qwen/Qwen2.5-Coder-7B"
    elif sys.argv[1] == "llama":
        model = "meta-llama/Llama-3.1-8B"
    # ['Qwen/Qwen2.5-Coder-7B', 'meta-llama/Llama-3.1-8B', 'meta-llama/Llama-3.1-8B-Instruct']
    grammar = "invariants.lark"
    Logger.log_info(f"Initializing model {model}")
    Logger.log_info(f"Initializing grammar {grammar}")
    llm = init(model, grammar)
    datasets_file = "benchmarks.txt"
    prompt = ("templates/system_text.txt", "templates/prompt_text.txt")
    num_samples = 15

    expt_logs = []
    try:
        expt_logs = main(llm, datasets_file, prompt, num_samples)
    except Exception as e:
        Logger.log_error(f"Error in main: {e}")
        new_expt_logs = {
            "error": str(e),
            "logs": expt_logs,
        }
    log_file_name = "logs/" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + "_expt_logs.json"
    with open(log_file_name, "w") as log_file:
        json.dump(expt_logs, log_file, indent=4)

    print(f"Logs saved to {log_file_name}")
