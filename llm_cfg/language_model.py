import time
from core.evaluation import filter_code, fix_indents
import transformers
import torch

class LanguageModel:
    def vocabulary(self) -> list[str]:
        raise NotImplementedError()

    def predict_tokens(self, prefix: str, n: int) -> list[int]:
        raise NotImplementedError()

    def predict_token(self, prefix: str, valid_tokens: list[int], top_k: int = 1) -> tuple[list[int], list[float]]:
        'Given prefix (prompt + already generated code), predicts next token'
        raise NotImplementedError()

    def tokenize(self, s: str) -> list[int]:
        raise NotImplementedError()

    def get_token(self, i: int) -> str:
        return self.vocabulary()[i]

    def predict_unconstrained(self, prefix: str, max_tokens: int, stop=None):
        raise NotImplementedError()


class HuggingFaceModel(LanguageModel):
    def __init__(self, model, prompt_template: str = '', api_key: str = None,
                 temperature: float = 0.0, top_p: float = 1.0, best_of: int = 1,
                 before_prediction_hook=lambda: None, tokenizer=None, device='cuda', logit_processors=None) -> None:
        super().__init__()

        self.prompt_template = prompt_template
        self.model = model
        self.tokenizer = tokenizer
        self.temperature = temperature
        self.top_p = top_p
        self.device = device
        self.best_of = best_of
        self._before_prediction_hook = before_prediction_hook
        self.logit_processors = logit_processors

        # self.vocab is a list of readable token strings (e.g., ' hello' and '\n')
        # sorted by their token IDs (so self.vocab[0] is the first token, etc).
        self.vocab = [v for k, v in
                      sorted([(t_id, self.tokenizer.decode([t_id]))
                              for _, t_id in self.tokenizer.get_vocab().items()])]

        # HACK: Is there a better way to know if a token has a prefix space?
        # We should only need this for LlamaTokenizer.
        if isinstance(self.tokenizer, transformers.LlamaTokenizer):
            for i in range(len(self.vocab)):
                t = self.vocab[i]
                if 2*len(t) != len(self.tokenizer.decode([i, i], add_special_tokens=False)):
                    self.vocab[i] = ' ' + t
                if t == '':
                    self.vocab[i] = ' '

    @torch.inference_mode()
    def generate_batch_completion(
        self, prompt, batch_size) -> list[str]:
        input_batch = [prompt for _ in range(batch_size)]
        inputs = self.tokenizer(input_batch, return_tensors="pt").to(self.model.device)
        input_ids_cutoff = inputs.input_ids.size(dim=1)

        start_time = time.time()

        generated_ids = self.model.generate(
            **inputs,
            use_cache=True,
            max_new_tokens=200,
            temperature=0.2,
            top_p=0.95,
            do_sample=True,
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.eos_token_id,  # model has no pad token
            logits_processor=self.logit_processors
        )

        last_token_id = len(generated_ids[0])
        if self.logit_processors is not None:
            python_decoder = self.logit_processors[0]
            last_token_id = python_decoder.last_valid_stage

        batch_completions = self.tokenizer.batch_decode(
            [ids[input_ids_cutoff:last_token_id] for ids in generated_ids],
            skip_special_tokens=True,
        )
        
        if self.logit_processors is not None:
            python_decoder = self.logit_processors[0]
            print(f"Time taken for generation: {time.time() - start_time:.2f}s")
            print(f"Token generation speed: {python_decoder.token_cnt / (time.time() - start_time):.2f} tokens/s")
            # print(f"Accept tokens sizes: {python_decoder.accept_tokens_sizes}")
        print('Completion:', batch_completions)

        return [filter_code(fix_indents(completion)) for completion in batch_completions]

    def tokenize(self, s: str) -> list[int]:
        return self.tokenizer.encode(s, add_special_tokens=False)

    def vocabulary(self) -> list[str]:
        return self.vocab

    def predict_token(self, prefix: str, valid_tokens: list[int], top_k: int = 1) -> tuple[list[int], list[float]]:
        input_ids = self.tokenizer.encode(prefix, return_tensors="pt", add_special_tokens=False)
        input_ids = input_ids.to(self.device)
        with torch.no_grad():
            logits = self.model(input_ids).logits[:, -1]
            valid_tokens_mask = torch.zeros(logits.shape[-1], dtype=torch.bool)
            valid_tokens_set = set(valid_tokens)
            if None in valid_tokens_set:
                valid_tokens_set.remove(None)
            valid_tokens = list(valid_tokens_set)
            # make sure there's no None in valid_tokens
            valid_tokens_mask[valid_tokens] = True
            logits = logits.squeeze(0)
            filtered_logits = logits.softmax(dim=-1)
            filtered_logits[~valid_tokens_mask] = 0
            filtered_logits = filtered_logits / filtered_logits.sum()

        top_values, top_indices = torch.topk(filtered_logits, top_k)
        top_indices = top_indices.tolist()
        top_values = top_values.log().tolist()
        
        return top_indices, top_values

    def predict_unconstrained(self, prefix: str, max_tokens: int, stop=None):
        prompt = f"{self.prompt_template}{prefix}"
        self._before_prediction_hook()
        input_ids = self.tokenizer.encode(
            prompt, return_tensors="pt", add_special_tokens=False)
        # Cut off inputs which are too long
        input_length = self.model.config.max_position_embeddings - max_tokens - 1
        if len(input_ids[0]) > input_length:
            input_ids = input_ids[:, -input_length:]
        input_ids = input_ids.to('cuda')
        with torch.cuda.amp.autocast():
            if self.temperature == 0.0:
                output = self.model.generate(
                    input_ids=input_ids,
                    max_new_tokens=max_tokens,
                    do_sample=False,
                )
            else:
                output = self.model.generate(
                    input_ids=input_ids,
                    max_new_tokens=max_tokens,
                    do_sample=True,
                    temperature=self.temperature,
                    top_p=self.top_p,
                )
            # remove the prompt
            output = output[:, len(input_ids[0]):]
        detokenized = self.tokenizer.decode(output[0])
        for stop_token in stop:
            if stop_token in detokenized:
                # split on the first stop token
                detokenized = detokenized.split(stop_token)[0]
        return detokenized
    