import common
from language_model import HuggingFaceModel
from transformers import (
    LlamaTokenizer,
    LlamaForCausalLM,
    AutoTokenizer,
    AutoModelForCausalLM,
    LogitsProcessorList
)
from utils import run_eval
import os
import torch
import argparse
from grammar_decoder import GrammarDecoder

# NOTE: List of currently downloaded models
# Llama models: "Llama-7b", "CodeLlama-7b", "CodeLlama-7b-Python", "Llama-13b"
# CodeGen models: "Salesforce/codegen-350m-multi", "Salesforce/codegen2-1b" 
# Bigcode models: "bigcode/starcoderbase-1b", "bigcode/santacoder" (1.1b WIP)
# WizardLM models: "WizardLM/WizardCoder-1B-V1.0"
# Replit models: replit/replit-code-v1-3b  (WIP: 'ReplitLMTokenizer' object has no attribute 'sp_model')

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["original", "grammar_mask", "synchromesh"], default="original")
    p.add_argument("--model", choices=["Llama-7b", "Llama-13b", "CodeLlama-7b", "CodeLlama-7b-Python"], default=None)
    p.add_argument("--model_id", type=str, default=None, help="model id for huggingface model hub")
    p.add_argument("--quantize", type=bool, default=True)
    p.add_argument("--gpu", type=int, default=1)
    p.add_argument("--num_samples", type=int, default=1)
    p.add_argument("--language", choices = ["python", "go"], default = "python", help = "language")
    p.add_argument("--dataset", choices = ["mbxp", "multi-humaneval", "mathqa-x"], default = "multi-humaneval", help = "dataset")
    args = p.parse_args()

    num_samples_per_task = args.num_samples
    
    # Load model
    device = f"cuda:{args.gpu}"
    
    if args.model_id is not None:
        tokenizer = AutoTokenizer.from_pretrained(args.model_id, cache_dir=common.HF_CACHE, token=common.HF_ACCESS_TOKEN, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(args.model_id, torch_dtype=torch.bfloat16, cache_dir=common.HF_CACHE, token=common.HF_ACCESS_TOKEN, trust_remote_code=True).eval().to(device)
        out_dir = f"results/{args.model_id}/{args.language}/{args.dataset}/"
    else:
        model_location = "/share/models/hugging_face/" + args.model
        tokenizer = LlamaTokenizer.from_pretrained(model_location)
        model = LlamaForCausalLM.from_pretrained(model_location, torch_dtype=torch.bfloat16).eval().to(device)
        out_dir = f"results/{args.model}/{args.language}/{args.dataset}/"
    
    out_path = out_dir + 'samples_' + str(num_samples_per_task) + '_mode_' + str(args.mode) + "_eval.jsonl"
    os.makedirs(out_dir, exist_ok=True)

    logit_processors = None
    if args.mode == 'grammar_mask':
        grammar_decoder = GrammarDecoder(args.language, tokenizer=tokenizer,)
        logit_processors = LogitsProcessorList([grammar_decoder])

    hf_model = HuggingFaceModel(model, tokenizer=tokenizer, device=device, logit_processors=logit_processors, mode=args.mode)

    run_eval(args, 
        hf_model,
        num_samples_per_task,
        out_path,
        format_tabs=True,
        )

    if args.mode == 'grammar_mask':
        print('Non matching token count: ', grammar_decoder.non_matching_token_cnt)
