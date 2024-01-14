from mxeval.data import write_jsonl, read_problems, get_data
from transformers import (
    PreTrainedModel,
    PreTrainedTokenizer,
)
from tqdm import tqdm
import typing
import common
import time
import os
import json

BatchGenerator = typing.Callable[
    [PreTrainedModel, PreTrainedTokenizer, str, int], list[str]
]

# reference: https://github.com/declare-lab/instruct-eval/blob/main/human_eval/main.py#L35
def filter_code(completion: str) -> str:
    # The program tends to overwrite, we only take the first function 
    completion = completion.lstrip("\n")
    return completion.split("\n\n")[0]


def fix_indents(text: str) -> str:
    return text.replace("\t", "    ")


def split_batch(samples: list[str], size=4):
    mini_batches = []

    for i in range(0, len(samples), size):
        mini_batches.append(samples[i : i + size])

    return mini_batches


def run_eval(args, 
    hf_model,
    num_samples_per_task: int,
    out_path: str,
    logger: common.Logger,
    format_tabs: bool = False,
):
    problems = get_data(args.dataset, args.language)
    samples = []
    pbar = tqdm(total=len(problems) * num_samples_per_task)
    count = 0
    start_time = time.time()
    for task_id in problems:
        if count == 10:
            break
        count += 1
        if format_tabs:
            prompt = problems[task_id]["prompt"].replace("    ", "\t")
        else:
            prompt = problems[task_id]["prompt"]

        batch_completions = hf_model.generate_batch_completion(prompt, num_samples_per_task)

        for i, completion in enumerate(batch_completions):
            result = dict(
                task_id=task_id,
                language=problems[task_id]["language"],
                completion=completion
            )
            samples += [result]
        
        pbar.update(num_samples_per_task)
    end_time = time.time() - start_time
    avg_time = end_time / count #len(problems)
    # print(avg_time)
    # avg_time_data = {"avg_time_generation" : avg_time}
    if args.model_id is not None:
        out_dir_time = f"results_time/{args.model_id}/{args.language}/{args.dataset}/{args.mode}/"
        # out_path_time = out_dir_time + 'max_length_' + str(args.max_length) + '_mode_' + str(args.mode) + "_time.jsonl"
        out_path_time_total = out_dir_time + '_mode_' + str(args.mode)+ '_no_inc_parse_'+ '_time.jsonl'
    else:
        out_dir_time = f"results_time/{args.model}/{args.language}/{args.dataset}/{args.mode}/"
        # out_path_time = out_dir_time + 'max_length_' + str(args.max_length) + '_mode_' + str(args.mode) + "_time.jsonl"
        out_path_time_total = out_dir_time + '_mode_' + str(args.mode)+'_no_inc_parse_'+'_time.jsonl'
    os.makedirs(out_dir_time, exist_ok=True)


    try:
        with open(out_path_time_total, 'r') as outfile:
            json_time = json.load(outfile)
    except (FileNotFoundError, json.JSONDecodeError):
    # If file does not exist or is not valid JSON, initialize json_decoded
        json_time = {}
    
    json_time[args.max_length] = avg_time

    with open(out_path_time_total, 'w') as json_file:
        json.dump(json_time, json_file)
    
    
    write_jsonl(out_path, samples)
