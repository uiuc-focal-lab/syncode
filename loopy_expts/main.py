import os
import json
import sys
from copy import deepcopy
from datetime import datetime
from typing import Tuple
from syncode import Syncode
from utils import Logger
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))


def init(model: str, grammar: str, device:str):
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


def parse_args(
    args: argparse.Namespace,
) -> Tuple[str, str, str, Tuple[str, str], int]:
    parser = argparse.ArgumentParser(
        description="Run experiments using Syncode on LLMs"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="meta-llama/CodeLlama-7b-Instruct-hf",
        choices=["meta-llama/CodeLlama-7b-Instruct-hf", "Qwen/Qwen2.5-Coder-7B", "meta-llama/Llama-3.1-8B", "meta-llama/Llama-3.1-8B-Instruct"],
        help="Model to use",
    )
    parser.add_argument(
        "--grammar",
        type=str,
        default="invariants.lark",
        help="Grammar to use",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="benchmarks.txt",
        help="File containing list of benchmarks",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="grammar_mask",
        choices=["original", "grammar_mask", "grammar_strict"],
        help="Mode to run the model in",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda:0",
        help="Device to run the model on",
    )
    parser.add_argument(
        "--num_samples",
        type=int,
        default=15,
        help="Number of samples to generate for each benchmark",
    )
    
    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    Logger.log_info(f"Initializing model {args.model}")
    Logger.log_info(f"Initializing grammar {args.grammar}")
    llm = init(args.model, args.grammar, args.device)
    prompt = ("templates/system_text.txt", "templates/prompt_text.txt")

    expt_logs = []
    try:
        expt_logs = main(llm, args.dataset, prompt, args.num_samples)
    except Exception as e:
        Logger.log_error(f"Error in main: {e}")
        new_expt_logs = {
            "error": str(e),
            "logs": expt_logs,
        }
    log_file_name = "logs/" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + "_expt_logs.json"
    grammar_text = None
    with open(args.grammar, "r") as grammar_file:
        grammar_text = grammar_file.read()
    expt_logs = {"params": vars(args), "logs": expt_logs}
    with open(log_file_name, "w") as log_file:
        json.dump(expt_logs, log_file, indent=4)

    print(f"Logs saved to {log_file_name}")
