import time
from language_model import HuggingFaceModel
from transformers import (
    LlamaTokenizer,
    LlamaForCausalLM,
    PreTrainedModel,
    PreTrainedTokenizer,
    LogitsProcessorList
)
from core import run_eval
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
    p.add_argument("--model_size", choices=["7B", "13B"], default="7B")
    p.add_argument("--quantize", type=bool, default=True)
    p.add_argument("--gpu", type=int, default=1)
    p.add_argument("--num_samples", type=int, default=1)
    p.add_argument("--language", choices = ["python", "go"], default = "python", help = "language")
    p.add_argument("--dataset", choices = ["mbxp", "multi-humaneval", "mathqa-x"], default = "multi-humaneval", help = "dataset")
    args = p.parse_args()

    num_samples_per_task = args.num_samples
    out_dir = f"results/llama/{args.language}/{args.dataset}/"
    out_path = out_dir + 'model_size' + str(args.model_size) +  '_samples_' + str(num_samples_per_task) + '_mode_' + str(args.mode) + "_eval.jsonl"
    os.makedirs(out_dir, exist_ok=True)

    # Load model
    device = f"cuda:{args.gpu}"
    model_location = "/share/models/llama_model/hf/" + args.model_size
    tokenizer = LlamaTokenizer.from_pretrained(model_location)
    model = LlamaForCausalLM.from_pretrained(model_location, torch_dtype=torch.bfloat16).eval().to(device)
    
    logit_processors = None
    if args.mode == 'grammar_mask':
        python_decoder = PythonDecoder(tokenizer=tokenizer,)
        logit_processors = LogitsProcessorList([python_decoder])

    hf_model = HuggingFaceModel(model, tokenizer=tokenizer, device=device, logit_processors=logit_processors, mode=args.mode)

    run_eval(args, 
        hf_model,
        num_samples_per_task,
        out_path,
        format_tabs=True,
        )

    if args.mode == 'grammar_mask':
        print('Non matching token count: ', python_decoder.non_matching_token_cnt)
