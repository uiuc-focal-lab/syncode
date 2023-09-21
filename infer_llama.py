import time
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


@torch.inference_mode()
def generate_batch_completion(
    model: PreTrainedModel, tokenizer: PreTrainedTokenizer, prompt, batch_size, logit_processors=None) -> list[str]:
    input_batch = [prompt for _ in range(batch_size)]
    inputs = tokenizer(input_batch, return_tensors="pt").to(model.device)
    input_ids_cutoff = inputs.input_ids.size(dim=1)

    start_time = time.time()

    generated_ids = model.generate(
        **inputs,
        use_cache=True,
        max_new_tokens=100,
        temperature=0.2,
        top_p=0.95,
        do_sample=True,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id,  # model has no pad token
        logits_processor=logit_processors
    )

    batch_completions = tokenizer.batch_decode(
        [ids[input_ids_cutoff:] for ids in generated_ids],
        skip_special_tokens=True,
    )
    
    if logit_processors is not None:
        python_decoder = logit_processors[0]
        print(f"Time taken for generation: {time.time() - start_time:.2f}s")
        print(f"Token generation speed: {python_decoder.token_cnt / (time.time() - start_time):.2f} tokens/s")
        print(f"Accept tokens sizes: {python_decoder.accept_tokens_sizes}")
    print('Completion:', batch_completions)

    return [filter_code(fix_indents(completion)) for completion in batch_completions]


if __name__ == "__main__":
    # Input grammar masking flag
    p = argparse.ArgumentParser()
    p.add_argument("--grammar_mask", action="store_true", default=False)
    args = p.parse_args()

    # adjust for n = 10 etc
    num_samples_per_task = 1
    out_dir = "results/llama/"
    out_path = out_dir + 'samples_' + str(num_samples_per_task) + '_grammar_' + str(args.grammar_mask) + "_eval.jsonl"
    os.makedirs(out_dir, exist_ok=True)

    tokenizer = LlamaTokenizer.from_pretrained("/share/models/llama_model/hf/7B")
    model = LlamaForCausalLM.from_pretrained("/share/models/llama_model/hf/7B", torch_dtype=torch.bfloat16).eval().to("cuda:1")

    logit_processors = None
    if args.grammar_mask:
        python_decoder = PythonDecoder(tokenizer=tokenizer,)
        logit_processors = LogitsProcessorList([python_decoder])

    run_eval(
        model,
        tokenizer,
        num_samples_per_task,
        out_path,
        generate_batch_completion,
        True,
        logit_processors = logit_processors,
        )