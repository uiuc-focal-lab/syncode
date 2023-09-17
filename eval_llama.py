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
from python_decoder import PythonDecoder

# TODO: move to python-dotenv
# add hugging face access token here
TOKEN = ""


@torch.inference_mode()
def generate_batch_completion(
    model: PreTrainedModel, tokenizer: PreTrainedTokenizer, prompt, batch_size) -> list[str]:
    input_batch = [prompt for _ in range(batch_size)]
    inputs = tokenizer(input_batch, return_tensors="pt").to(model.device)
    input_ids_cutoff = inputs.input_ids.size(dim=1)

    python_decoder = PythonDecoder(
        tokenizer=tokenizer,)

    generated_ids = model.generate(
        **inputs,
        use_cache=True,
        max_new_tokens=200,
        temperature=0.2,
        top_p=0.95,
        do_sample=True,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id,  # model has no pad token
        logits_processor=LogitsProcessorList([python_decoder])
    )

    batch_completions = tokenizer.batch_decode(
        [ids[input_ids_cutoff:] for ids in generated_ids],
        skip_special_tokens=True,
    )

    return [filter_code(fix_indents(completion)) for completion in batch_completions]


if __name__ == "__main__":
    # adjust for n = 10 etc
    num_samples_per_task = 1
    out_path = "results/llama/eval.jsonl"
    os.makedirs("results/llama", exist_ok=True)

    tokenizer = LlamaTokenizer.from_pretrained("/share/models/llama_model/hf/7B")
    model = LlamaForCausalLM.from_pretrained("/share/models/llama_model/hf/7B", torch_dtype=torch.bfloat16).eval().to("cuda:1")

    run_eval(
        model,
        tokenizer,
        num_samples_per_task,
        out_path,
        generate_batch_completion,
        True,)