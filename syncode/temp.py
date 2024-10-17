
# Test speeds of various LLMs on CPU and GPU
import time
import common

# Load model
def run_model(model_name, prompt: str, device: str, quantize: bool):
    model = common.load_model(model_name, device, quantize)
    tokenizer = common.load_tokenizer(model_name)
    
    model = model.to(device)
    
    input_ids = tokenizer.encode(prompt, return_tensors='pt').to(device)

    start_time = time.time()
    output = model.generate(input_ids, max_new_tokens=100)
    end_time = time.time()

    total_time = end_time - start_time
    num_tokens = len(tokenizer.decode(output[0], skip_special_tokens=True))
    tokens_per_sec = num_tokens / total_time

    print("Results for:", model_name, "device =", device, "with quantize =", quantize, flush=True)
    print(f"Time taken: {end_time - start_time:.2f}s", flush=True)
    print(f"Number of tokens: {num_tokens}", flush=True)
    print(f"Tokens per second: {tokens_per_sec:.2f}", flush=True)


models = models = ["Qwen/Qwen2.5-0.5B", "Qwen/Qwen2.5-1.5B", "Qwen/Qwen2.5-Coder-1.5B", "Qwen/Qwen2.5-1.5B-Instruct", "Qwen/Qwen2.5-Coder-7B", "meta-llama/Llama-3.2-1B", "meta-llama/Llama-3.2-3B"]
devices = ["cpu", "cuda"]
quantizations = [True, False]

for model_name in models:
    for device in devices:
        for quantize in quantizations:
            run_model(model_name, "1, 2, 3, 4", device, quantize)
