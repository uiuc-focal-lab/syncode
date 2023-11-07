import time
from utils.evaluation import filter_code, fix_indents
from transformers import LlamaTokenizer
import common
from synchromesh.completion_engine import LarkCompletionEngine
from synchromesh.synchromesh import StreamingCSD
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
                 before_prediction_hook=lambda: None, tokenizer:LlamaTokenizer=None, device='cuda', logit_processors=None, 
                 mode: str ='original') -> None:
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
        self.mode = mode
        self.vocab = common.get_vocab_from_tokenizer(self.tokenizer)

    def generate_batch_completion(self, prompt, batch_size, mode='original') -> list[str]:
        if self.mode == 'synchromesh':
            return self.generate_batch_completion_synchromesh(prompt, batch_size)
        else:
            return self.generate_batch_completion_grammar(prompt, batch_size)

    @torch.inference_mode()
    def generate_batch_completion_grammar(self, prompt, batch_size) -> list[str]:
        '''
        Generates batch_size completions for the given prompt of human-eval. 
        '''
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


        last_token_id = [len(generated_ids[i]) for i in range(batch_size)]
        if self.logit_processors is not None:
            python_decoder = self.logit_processors[0]
            last_token_id = [python_decoder.last_valid_state[i] for i in range(batch_size)]
        
        batch_completions = [
            self.tokenizer.decode(ids[input_ids_cutoff-1:last_token_id[i]], skip_special_tokens=True)[1:] for i, ids in enumerate(generated_ids)
        ]

        if self.logit_processors is not None:
            python_decoder = self.logit_processors[0]
            print(f"Time taken for generation: {time.time() - start_time:.2f}s")
            print(f"Token generation speed: {python_decoder.token_cnt / (time.time() - start_time):.2f} tokens/s")
            # print(f"Accept tokens sizes: {python_decoder.accept_tokens_sizes}")
        print('Completion:', batch_completions)

        return [filter_code(fix_indents(completion)) for completion in batch_completions]

    def generate_batch_completion_synchromesh(self, prompt, batch_size) -> list[str]:
        '''
        Generates batch_size completions for the given prompt of human-eval using Synchromesh. 
        '''
        comp_engine = LarkCompletionEngine('dict', True)
        csd = StreamingCSD(comp_engine, self.vocabulary(), prefix=prompt)
        start_time = time.time()

        while not comp_engine.is_complete(csd.get_current_prediction()):
            next_token = self.predict_unconstrained(csd.get_current_prediction(), max_tokens=1)
            # print(type(continuation), repr(continuation))
            # tokens = self.tokenize(continuation)
            # print(type(tokens) ,tokens, [csd._vocab[t] for t in tokens])
            # print(tokens[0], csd.can_token_follow(tokens[0]))
            if csd.can_token_follow(next_token):
                csd.feed_prediction(next_token)
            else:
                print('Cannot follow token:', csd._vocab[next_token])
                valid_tokens = csd.get_valid_tokens()
                tokens, _ = self.predict_token(csd.get_current_prediction(), valid_tokens)
                print('valid tokens:', [csd._vocab[t] for t in tokens])
                print('Predicted token:', csd._vocab[tokens[0]])
                csd.feed_prediction(tokens[0])
            s = csd.get_current_prediction()
            if len(s) > 500:
                break
            csd.fast_forward()

        delta = time.time() - start_time
        print('Predicted:', repr(csd.get_current_prediction()))
        print('Throughput:', len(csd.get_current_prediction_tokens()) / delta, 'tokens/s')

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
        print('Prompt:', prompt)
        print(repr(prompt))
        
        self._before_prediction_hook()
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt", add_special_tokens=False)

        # Cut off inputs which are too long
        input_length = self.model.config.max_position_embeddings - max_tokens - 1
        if len(input_ids[0]) > input_length:
            input_ids = input_ids[:, -input_length:]
        input_ids = input_ids.to(self.device)
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
        # print('Here is the output:', output[0])
        # detokenized = self.tokenizer.decode(output[0])
        # if stop is not None:
        #     for stop_token in stop:
        #         if stop_token in detokenized:
        #             # split on the first stop token
        #             detokenized = detokenized.split(stop_token)[0]
        return output[0]
    