import time
from language_model import HuggingFaceModel
from transformers import (
    LlamaTokenizer,
    LlamaForCausalLM,
    PreTrainedModel,
    PreTrainedTokenizer,
    LogitsProcessorList
)
from core import filter_code, run_eval, fix_indents
import os
import torch
import argparse
from python_decoder import PythonDecoder

# TODO: move to python-dotenv
# add hugging face access token here
TOKEN = ""

if __name__ == "__main__":
    # Input grammar masking flag
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["original", "grammar_mask", "synchromesh"], default="original")
    args = p.parse_args()

    # adjust for n = 10 etc
    num_samples_per_task = 1
    out_dir = "results/llama/"
    out_path = out_dir + 'samples_' + str(num_samples_per_task) + '_mode_' + str(args.mode) + "_eval.jsonl"
    os.makedirs(out_dir, exist_ok=True)

    device = "cuda:1"
    tokenizer = LlamaTokenizer.from_pretrained("/share/models/llama_model/hf/7B")
    model = LlamaForCausalLM.from_pretrained("/share/models/llama_model/hf/7B", torch_dtype=torch.bfloat16).eval().to(device)
    
    logit_processors = None
    if args.mode == 'grammar_mask':
        python_decoder = PythonDecoder(tokenizer=tokenizer,)
        logit_processors = LogitsProcessorList([python_decoder])

    hf_model = HuggingFaceModel(model, tokenizer=tokenizer, device=device, logit_processors=logit_processors, mode=args.mode)

    run_eval(
        hf_model,
        num_samples_per_task,
        out_path,
        format_tabs=True,
        )

    if args.mode == 'grammar_mask':
        print('Non matching token count: ', python_decoder.non_matching_token_cnt)
