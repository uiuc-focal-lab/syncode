import time
from parsers.grammars.grammar import Grammar
from utils.generation import filter_code, fix_indents
import common
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
    def __init__(
            self, 
            model, 
            grammar: Grammar,
            logger: common.Logger, 
            tokenizer=None, 
            prompt_template: str = '', 
            api_key: str = None, 
            best_of: int = 1, 
            before_prediction_hook=lambda: None, 
            device='cuda', 
            logit_processors=None, 
            mode: str ='original', 
            **kwargs) -> None:
        super().__init__()

        self.prompt_template = prompt_template
        self.model = model
        self.logger = logger
        self.tokenizer = tokenizer
        self.device = device
        self.best_of = best_of
        self._before_prediction_hook = before_prediction_hook
        self.logit_processors: list = logit_processors
        self.mode = mode
        self.grammar = grammar
        self.vocab = common.get_vocab_from_tokenizer(self.tokenizer)
        self.gen_kwargs = kwargs

    def get_grammar_decoder(self):
        if self.logit_processors is not None and len(self.logit_processors) > 0:
            return self.logit_processors[0]
        return None

    @torch.inference_mode()
    def generate_batch_completion_grammar(self, prompt, batch_size) -> list[str]:
        '''
        Generates batch_size completions for the given prompt. 
        '''
        input_batch = [prompt for _ in range(batch_size)]
        inputs = self.tokenizer(input_batch, return_tensors="pt").to(self.model.device)
        input_ids_cutoff = inputs.input_ids.size(dim=1)

        start_time = time.time()

        generated_ids = self.model.generate(
            **inputs,
            logits_processor=self.logit_processors,
            **self.gen_kwargs
        )
        grammar_decoder = self.get_grammar_decoder()
        batch_completions = []

        for i in range(batch_size):
            raw_completion = self.tokenizer.decode(generated_ids[i][input_ids_cutoff:len(generated_ids[i])], skip_special_tokens=True)                                       
            self.logger.log_code("Raw completion", raw_completion)

            # Post-processing to filter out using stop word (e.g. "\n\n")
            if self.grammar.name == "python":
                completion = self.postproces_completion_python(i, batch_size, input_ids_cutoff, generated_ids, grammar_decoder, raw_completion)
            elif self.grammar.name == "go": 
                completion = self.postproces_completion_go(i, batch_size, raw_completion, generated_ids, grammar_decoder, input_ids_cutoff)
            else: # TODO: handle the case for other grammars
                completion = raw_completion

            self.logger.log_code("Filtered sample", completion)
            batch_completions.append(completion)

        if grammar_decoder is not None:
            self.logger.log_time(f"Time taken for generation: {time.time() - start_time:.2f}s")
            self.logger.log(f"Token generation speed: {grammar_decoder.token_cnt / (time.time() - start_time):.2f} tokens/s")
        self.logger.log(f"Completion: {batch_completions}")

        return batch_completions

    def postproces_completion_python(self, i, batch_size, input_ids_cutoff, generated_ids, grammar_decoder, raw_completion):
        stop_word = "\n\n"
        if stop_word in raw_completion or self.tokenizer.eos_token_id == generated_ids[i][-1] or grammar_decoder is None:
            completion = filter_code(fix_indents(raw_completion))
        else:
            # Use when the stop word does not exist in the completion and grammar_decoder is used
            function_incomplete = [False for _ in range(batch_size)]
            completion = self.compute_backup_completion(grammar_decoder, function_incomplete, i, input_ids_cutoff, generated_ids)
        return completion

    def postproces_completion_go(self, i, batch_size, raw_completion, generated_ids, grammar_decoder, input_ids_cutoff):
        stop_word = "\n\n"
        if self.mode == "original" or stop_word in raw_completion or self.tokenizer.eos_token_id == generated_ids[i][-1]: 
            # only filter with stop-word for original mode
            completion = filter_code(raw_completion)
        else:
            # Use when the stop word does not exist in the completion and grammar_decoder is used
            function_incomplete = [False for _ in range(batch_size)]
            self.logger.log(f"Function incomplete!")
            completion = self.compute_backup_completion(grammar_decoder, function_incomplete, i, input_ids_cutoff, generated_ids)

            if function_incomplete[i]:
                # if the function is incomplete, then we need to add a closing brace
                completion += "}"

        return completion

    def compute_backup_completion(self, grammar_decoder, function_incomplete, i, input_ids_cutoff, generated_ids):
        self.logger.log(f"Last valid state: {grammar_decoder.last_valid_state[i]}")
        self.logger.log(f"Function end: {grammar_decoder.function_end[i]}")

        if grammar_decoder.function_end[i] is not None:
            # if the function end is not None, then the last valid state is the function end
            last_token_id = grammar_decoder.function_end[i]
        else:
            # otherwise, the last valid state is the last valid state
            function_incomplete[i] = True
            last_token_id = grammar_decoder.last_valid_state[i]
        # return last_token_id
        # Use when the stop word does not exist in the completion
        backup_completion = self.tokenizer.decode(generated_ids[i][input_ids_cutoff-1:last_token_id],
        skip_special_tokens=True)[1:]  
        return backup_completion
    
    def tokenize(self, s: str) -> 'list[int]':
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
    