import time
from utils.generation import filter_code, fix_indents
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
    def __init__(self, model, logger: common.Logger, prompt_template: str = '', api_key: str = None,
                 temperature: float = 0.0, top_p: float = 1.0, best_of: int = 1, max_new_tokens: int = 400, 
                 before_prediction_hook=lambda: None, tokenizer:LlamaTokenizer=None, device='cuda', logit_processors=None, 
                 mode: str ='original', language: str = 'python') -> None:
        super().__init__()

        self.prompt_template = prompt_template
        self.model = model
        self.logger = logger
        self.tokenizer = tokenizer
        self.temperature = temperature
        self.top_p = top_p
        self.max_new_tokens = max_new_tokens
        self.device = device
        self.best_of = best_of
        self._before_prediction_hook = before_prediction_hook
        self.logit_processors: list = logit_processors
        self.mode = mode
        self.language = language
        self.vocab = common.get_vocab_from_tokenizer(self.tokenizer)

    def get_grammar_decoder(self):
        if len(self.logit_processors) > 0:
            return self.logit_processors[0]
        return None

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
            max_new_tokens=self.max_new_tokens,
            temperature=0.2,
            top_p=0.95,
            do_sample=True,
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.eos_token_id,  # model has no pad token
            logits_processor=self.logit_processors
        )

        grammar_decoder = self.get_grammar_decoder()
        batch_completions = []

        for i in range(batch_size):
            last_token_id = len(generated_ids[i])
            if grammar_decoder is not None:
                self.logger.log(f"Last valid state: {grammar_decoder.last_valid_state[i]}")
                self.logger.log(f"Function end: {grammar_decoder.function_end[i]}")

                if grammar_decoder.function_end[i] is not None:
                    # if the function end is not None, then the last valid state is the function end
                    last_token_id = grammar_decoder.function_end[i]
                else:
                    # otherwise, the last valid state is the last valid state
                    last_token_id = grammar_decoder.last_valid_state[i]

            completion = self.tokenizer.decode(generated_ids[i][input_ids_cutoff-1:last_token_id],
             skip_special_tokens=True)[1:]

            # Can remove this logging in future
            raw_completion = self.tokenizer.decode(generated_ids[i][input_ids_cutoff-1:len(generated_ids[i])], skip_special_tokens=True)[1:]                                       
            self.logger.log_code("Raw completion", raw_completion)

            # Post-processing to filter out using stop word (e.g. "\n\n")
            if self.language == "python": 
                completion = filter_code(fix_indents(completion))
            elif self.language == "go" and self.mode == "original": 
                # only filter with stop-word for original mode
                completion = filter_code(completion)

            self.logger.log_code("Filtered sample", completion)
            batch_completions.append(completion)

        if grammar_decoder is not None:
            self.logger.log(f"Time taken for generation: {time.time() - start_time:.2f}s")
            self.logger.log(f"Token generation speed: {grammar_decoder.token_cnt / (time.time() - start_time):.2f} tokens/s")
        self.logger.log(f"Completion: {batch_completions}")

        return batch_completions

    def generate_batch_completion_synchromesh(self, prompt, batch_size) -> list[str]:
        '''
        Generates batch_size completions for the given prompt of human-eval using Synchromesh. 
        '''
        comp_engine = LarkCompletionEngine('dict', True)
        csd = StreamingCSD(comp_engine, self.vocabulary(), prefix=prompt)
        start_time = time.time()

        while not comp_engine.is_complete(csd.get_current_prediction()):
            next_token = self.predict_unconstrained(csd.get_current_prediction(), max_tokens=1)
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
        return [csd.get_current_prediction()]

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
    