import time
from syncode.parsers.grammars import Grammar
from syncode.utils.generation import filter_code, fix_indents
import syncode.common as common
import torch
from typing import Iterable, Tuple
from syncode.parsers import create_parser
from syncode.dfa_mask_store import DFAMaskStore

class LanguageModel:
    def vocabulary(self) -> Iterable[str]:
        raise NotImplementedError()

    def predict_tokens(self, prefix: str, n: int) -> Iterable[int]:
        raise NotImplementedError()

    def predict_token(self, prefix: str, valid_tokens: Iterable[int], top_k: int = 1) -> Tuple[Iterable[int], Iterable[float]]:
        'Given prefix (prompt + already generated code), predicts next token'
        raise NotImplementedError()

    def tokenize(self, s: str) -> Iterable[int]:
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
            parser='lalr',
            num_samples=1,
            chat_mode=False,
            use_cache=True,
            dfa_mask_store = None,
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
        self.parser = parser
        self.num_samples = num_samples
        self.chat_mode = chat_mode
        self.use_cache = use_cache
        self.batch_size = num_samples

        # Load dfa mask store
        # self.dfa_mask_store = DFAMaskStore.load_dfa_mask_store(
        #                             grammar=self.grammar, 
        #                             tokenizer=self.tokenizer, 
        #                             use_cache=self.use_cache,
        #                             logger=self.logger 
        #                             # logger=self.logger
        #                             )

        if dfa_mask_store is not None:
            self.dfa_mask_store = dfa_mask_store
        # Create parsers
        self.inc_parsers = [create_parser(self.grammar,logger=self.logger, parser=parser) for _ in range(self.batch_size)]
        self.function_end = []
        self.last_valid_state = []
        self.start_from = None
        # self.partial_code_trace = []

    
    def reset(self):
        """
        Resets the decoder state on every new prompt.
        """
        self.last_valid_state = [0 for _ in range(self.batch_size)]
        self.function_end = [None for _ in range(self.batch_size)]
        # self.partial_codes_trace = []
        # self.token_cnt = 0
        self.start_from = None 
        for p in self.inc_parsers:
            p.reset()


    def get_grammar_decoder(self):
        if self.logit_processors is not None and len(self.logit_processors) > 0:
            return self.logit_processors[0]
        return None

    @torch.inference_mode()
    def generate_batch_completion_grammar(self, prompt, batch_size) -> Iterable[str]:
        '''
        Generates batch_size completions for the given prompt. 
        '''
        input_batch = [prompt for _ in range(batch_size)]
        inputs = self.tokenizer(input_batch, return_tensors="pt").to(self.model.device)
        input_ids_cutoff = inputs.input_ids.size(dim=1)

        start_time = time.time()
        if self.mode == "original":
            generated_ids = self.model.generate(
                **inputs,
                **self.gen_kwargs
            )

        elif self.mode == "grammar_mask":
            generated_ids, function_end, last_valid_state = self.model.generate(
                **inputs,
                syncode = self.mode,
                parser = self.parser,
                num_samples = self.num_samples,
                chat_mode = self.chat_mode,
                use_cache = self.use_cache,
                tokenizer = self.tokenizer,
                logger_sync = self.logger,
                dfa_mask_store = self.dfa_mask_store,
                inc_parsers = self.inc_parsers,
                function_end = self.function_end,
                last_valid_state = self.last_valid_state,
                grammar = self.grammar,
                device = self.device,
                # partial_code_trace = self.partial_code_trace,
                **self.gen_kwargs
            )
            self.function_end = function_end
            self.last_valid_state = last_valid_state

        # self.function_end = function_end
        # self.last_valid_state = last_valid_state
        # print(function_end, last_valid_state)
        # grammar_decoder = self.get_grammar_decoder()
        grammar_decoder = self.mode == 'grammar_masking'
        batch_completions = []

        for i in range(batch_size):
            raw_completion = self.tokenizer.decode(generated_ids[i][input_ids_cutoff:len(generated_ids[i])], skip_special_tokens=True)                                       
            self.logger.log_code("Raw completion", raw_completion)

            if self.grammar.name == "python":
                completion = self.postproces_completion_python(i, batch_size, input_ids_cutoff, generated_ids, raw_completion)
            elif self.grammar.name == "go": 
                completion = self.postproces_completion_go(i, batch_size, raw_completion, generated_ids, input_ids_cutoff)
            else: # TODO: handle the case for other grammars
                completion = raw_completion                

            self.logger.log_code("Filtered sample", completion)
            batch_completions.append(completion)

        if self.mode == "grammar_mask":
            self.logger.log_time(f"Time taken for generation: {time.time() - start_time:.2f}s")
            # self.logger.log(f"Token generation speed: {grammar_decoder.token_cnt / (time.time() - start_time):.2f} tokens/s")
        self.logger.log(f"Completion: {batch_completions}")

        return batch_completions

    @torch.inference_mode()
    def generate_chat_completion_grammar(self, prompt) -> str:
        '''
        Generates chat completion for the given prompt. 
        '''
        assert 'apply_chat_template' in dir(self.tokenizer), "Tokenizer does not support chat completion"

        message = [{"role": "user", "content": prompt}]
        inputs = self.tokenizer.apply_chat_template(
            message, 
            add_generation_prompt=True, 
            return_tensors="pt"
            ).to(self.model.device)
        
        input_ids_cutoff = inputs.size(dim=1)

        # input_ids_cutoff = inputs.input_ids.size(dim=1)
        start_time = time.time()

        if self.mode == "original":
            generated_ids = self.model.generate(
                **inputs,
                **self.gen_kwargs
            )

        elif self.mode == "grammar_mask":
            generated_ids, function_end, last_valid_state = self.model.generate(
                **inputs,
                syncode = self.mode,
                parser = self.parser,
                num_samples = self.num_samples,
                chat_mode = self.chat_mode,
                use_cache = self.use_cache,
                tokenizer = self.tokenizer,
                logger_sync = self.logger,
                dfa_mask_store = self.dfa_mask_store,
                inc_parsers = self.inc_parsers,
                function_end = self.function_end,
                last_valid_state = self.last_valid_state,
                **self.gen_kwargs
            )
        completion = self.tokenizer.decode(
            generated_ids[0][input_ids_cutoff:len(generated_ids[0])], 
            skip_special_tokens=True)

        self.logger.log_code("Raw completion", completion)
        return completion


    def postproces_completion_python(self, i, batch_size, input_ids_cutoff, generated_ids, raw_completion):
        stop_word = "\n\n"
        if stop_word in raw_completion or self.tokenizer.eos_token_id == generated_ids[i][-1] or self.mode != "grammar_mask":
            completion = filter_code(fix_indents(raw_completion))
        else:
            # Use when the stop word does not exist in the completion and grammar_decoder is used
            function_incomplete = [False for _ in range(batch_size)]
            completion = self.compute_backup_completion( function_incomplete, i, input_ids_cutoff, generated_ids)
        return completion


    def postproces_completion_go(self, i, batch_size, raw_completion, generated_ids, input_ids_cutoff):
        extra_stop_word = "\n\n"
        
        if self.mode == "original": 
            # only filter with stop-word for original mode
            completion = filter_code(raw_completion, extra_stop_word=extra_stop_word)
        else:
            # When the grammar_decoder is used
            function_incomplete = [False for _ in range(batch_size)]
            self.logger.log(f"Function incomplete!")
            completion = self.compute_backup_completion(function_incomplete, i, input_ids_cutoff, generated_ids)

            if function_incomplete[i]:
                # if the function is incomplete, then we need to add a closing brace
                completion += "}"

        return completion

    def compute_backup_completion(self, function_incomplete, i, input_ids_cutoff, generated_ids):
        self.logger.log(f"Last valid state: {self.last_valid_state[i]}")
        self.logger.log(f"Function end: {self.function_end[i]}")

        if self.function_end[i] is not None:
            # if the function end is not None, then the last valid state is the function end
            last_token_id = self.function_end[i]
        else:
            # otherwise, the last valid state is the last valid state
            function_incomplete[i] = True
            last_token_id = self.last_valid_state[i]
        # return last_token_id
        # Use when the stop word does not exist in the completion
        backup_completion = self.tokenizer.decode(generated_ids[i][input_ids_cutoff-1:last_token_id],
        skip_special_tokens=True)[1:]  
        return backup_completion
    
    def tokenize(self, s: str) -> 'Iterable[int]':
        return self.tokenizer.encode(s, add_special_tokens=False)

    def vocabulary(self) -> Iterable[str]:
        return self.vocab

    def predict_token(self, prefix: str, valid_tokens: Iterable[int], top_k: int = 1) -> Tuple[Iterable[int], Iterable[float]]:
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
    
