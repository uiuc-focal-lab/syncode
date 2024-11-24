import time
import torch
import syncode.common as common
from syncode.grammar_decoder import SyncodeLogitsProcessor
from transformers import LogitsProcessorList, StoppingCriteriaList, StoppingCriteria
from syncode.parsers.grammars import Grammar
from syncode.utils.generation import filter_code, fix_indents
from typing import Callable, Iterable, Union
from transformers.generation.utils import GenerationMode
from transformers.generation.configuration_utils import GenerationConfig


class KeywordsStoppingCriteria(StoppingCriteria):
    '''
    Assume batch_size = 1

    We can use this class to check if the stop word is present in the completion. This is more expensive since we need to decode the completion to check if the stop word is present.
    '''
    def __init__(self, tokenizer, stop_words = []):
        super().__init__()
        self.tokenizer = tokenizer
        self.stop_words = stop_words
        self.stop_words_ids = []

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> bool:
        partial_output = self.tokenizer.batch_decode(input_ids, skip_special_tokens=True)[0]
        for stop_word in self.stop_words:
            if partial_output.endswith(stop_word):
                return True
        return False    


class HuggingFaceModel:
    def __init__(
            self, 
            model: Callable, 
            grammar: Grammar,
            tokenizer=None, 
            prompt_template: str = '', 
            best_of: int = 1, 
            before_prediction_hook=lambda: None, 
            device='cuda', 
            grammar_decoder=None, 
            mode: str ='original', 
            **kwargs) -> None:
        super().__init__()

        self.prompt_template = prompt_template
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        self.best_of = best_of
        self._before_prediction_hook = before_prediction_hook
        self.grammar_decoder = grammar_decoder
        self.logit_processors: Iterable = LogitsProcessorList([self.grammar_decoder]) if self.grammar_decoder is not None else None
        self.mode = mode
        self.grammar = grammar
        self.vocab = common.get_vocab_from_tokenizer(self.tokenizer)
        self.gen_args = kwargs

    def get_grammar_decoder(self):
        if self.logit_processors is not None and len(self.logit_processors) > 0:
            return self.logit_processors[0]
        return None

    @torch.inference_mode()
    def generate_batch_completion_grammar(self, prompt: Union[str, list], batch_size, stop_words=None) -> Iterable[str]:
        '''
        Generates batch_size completions for the given prompt. 
        '''
        # Reset the grammar decoder
        if self.grammar_decoder is not None:
            self.grammar_decoder.reset(prompt)

        if (isinstance(prompt, str)):
            input_batch = [prompt for _ in range(batch_size)]
            inputs = self.tokenizer(input_batch, return_tensors="pt").to(self.device)
        elif (isinstance(prompt, list)):
            inputs = self.tokenizer.apply_chat_template(
                prompt, 
                add_generation_prompt=True, 
                return_tensors="pt",
                return_dict=True
            ).to(self.device)
        
        input_ids_cutoff = inputs.input_ids.size(dim=1)
        
        # Get the generation config
        gen_config = GenerationConfig.from_model_config(self.model.config)
        gen_config.update(**self.gen_args)

        # Get the generation mode
        gen_mode = self._get_generation_mode(gen_config)

        # Create stopping criteria
        if stop_words is not None:
            stopping_criteria = StoppingCriteriaList([KeywordsStoppingCriteria(self.tokenizer, stop_words=stop_words)])
        else:
            stopping_criteria = []

        # Generate completions
        if (gen_mode == GenerationMode.SAMPLE or gen_mode == GenerationMode.GREEDY_SEARCH) and True: # Use our own implementation for greedy search and sampling
            generated_ids = self._generate(
                inputs, 
                gen_config, 
                gen_mode, 
                grammar_decoder=self.grammar_decoder,
                stopping_criteria=stopping_criteria
                )
        else:
            # Use generate from transformers library for other modes
            generated_ids = self.model.generate(
                **inputs, 
                logits_processor=self.logit_processors, 
                stop_strings=stop_words,
                tokenizer=self.tokenizer,
                **self.gen_args
                )
        batch_completions = []

        # Total tokens generated
        self.total_tokens = 0
        for i in range(batch_size):
            self.total_tokens += len(generated_ids[i])-input_ids_cutoff+1

        # TODO: Move this to CodeEval
        for i in range(batch_size):
            raw_completion = self.tokenizer.decode(generated_ids[i][input_ids_cutoff:len(generated_ids[i])], skip_special_tokens=True)                                       

            # Post-processing to filter out using stop word (e.g. "\n\n")
            if self.grammar != None and self.grammar.name == "python":
                completion = self.postproces_completion_python(i, batch_size, input_ids_cutoff, generated_ids, self.grammar_decoder, raw_completion)
            elif self.grammar != None and self.grammar.name == "go": 
                completion = self.postproces_completion_go(i, batch_size, raw_completion, generated_ids, self.grammar_decoder, input_ids_cutoff)
            else: # TODO: handle the case for other grammars
                completion = raw_completion

            batch_completions.append(completion)
        
        return batch_completions

    @torch.inference_mode()
    def _generate(
        self, 
        inputs:dict, 
        gen_config:GenerationConfig, 
        gen_mode:GenerationMode, 
        grammar_decoder:SyncodeLogitsProcessor=None,
        stopping_criteria:StoppingCriteria=[]
        ):
        """
        We support greedy search and sampling for batch size 1 otherwise we use the generate function from transformers library.
        """
        token_ids, attention_mask, past_key_values = inputs['input_ids'], inputs['attention_mask'], None
        logit_warper = self.model._get_logits_warper(gen_config, device=self.device)
        max_tokens = self.gen_args['max_new_tokens']+token_ids.size(1)
        num_outputs = token_ids.size(0)
        unfinished_sequences = torch.ones(num_outputs, dtype=torch.long, device=self.device)
        this_peer_finished = False
        
        while not this_peer_finished:
            try:
                if past_key_values: # Get the last token if kv is cached for all previous tokens
                    input_ids = token_ids[..., -1].unsqueeze(-1) 
                else:
                    input_ids = token_ids

                outputs = self.model(
                    input_ids, 
                    attention_mask=attention_mask, 
                    past_key_values=past_key_values
                    )                
            except IndexError as e:  
                raise ValueError(f"The input length exceeds the context length of the model. {e}")

            next_token_scores, past_key_values = outputs.logits[:, -1, :], outputs.past_key_values
            
            if grammar_decoder is not None:
                # batch of next tokens
                next_tokens = self._get_next_token(gen_mode, token_ids, logit_warper, next_token_scores)
                
                for idx in range(token_ids.size(0)):
                    token_ids_i = token_ids[idx:idx+1]
                    next_token_scores_i = next_token_scores[idx:idx+1]
                    next_token_i = next_tokens[idx:idx+1]

                    is_valid = grammar_decoder.is_valid(token_ids_i, next_token_i)

                    if not is_valid:
                        # calling grammar decoder is expensive. Hence, in the opportunist mode, we call it only when the standard generation is syntactically incorrect
                        next_token_scores_i = grammar_decoder(token_ids_i, next_token_scores_i)
                        next_tokens[idx] = self._get_next_token(gen_mode, token_ids_i, logit_warper, next_token_scores_i)
            else:
                next_tokens = self._get_next_token(gen_mode, token_ids, logit_warper, next_token_scores)
            

            # Update the next token
            next_tokens = next_tokens * unfinished_sequences + self.tokenizer.eos_token_id * (1 - unfinished_sequences)

            token_ids = torch.cat([token_ids, next_tokens[:, None]], dim=-1)
                    
             # Check if the next token is the end of the sequence or the max tokens is reached
            if token_ids.size(1) >= max_tokens:
                break

            # Update attention mask
            attention_mask = torch.cat([attention_mask, torch.ones((attention_mask.size(0), 1), dtype=attention_mask.dtype).to(self.device)], dim=-1)

            # Update the unfinished sequences
            unfinished_sequences = unfinished_sequences & ~(stopping_criteria(token_ids, next_token_scores) | (token_ids[:, -1] == self.tokenizer.eos_token_id))
            this_peer_finished = unfinished_sequences.max() == 0
            
        return token_ids

    def _get_next_token(self, gen_mode, token_ids, logit_warper, next_token_scores):
        if gen_mode == GenerationMode.GREEDY_SEARCH:
            next_token = torch.argmax(next_token_scores, dim=-1)
        elif gen_mode == GenerationMode.SAMPLE:
            next_token_scores = logit_warper(token_ids, next_token_scores)
            probs = torch.nn.functional.softmax(next_token_scores, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1).squeeze(1)
        return next_token

    def _get_generation_mode(
        self, generation_config: GenerationConfig
    ) -> GenerationMode:
        """
        Returns the generation mode triggered by a [`GenerationConfig`] instance.
        """
        if generation_config.constraints is not None or generation_config.force_words_ids is not None:
            generation_mode = GenerationMode.CONSTRAINED_BEAM_SEARCH
        elif generation_config.num_beams == 1:
            if generation_config.do_sample is False:
                if (
                    generation_config.top_k is not None
                    and generation_config.top_k > 1
                    and generation_config.penalty_alpha is not None
                    and generation_config.penalty_alpha > 0
                ):
                    generation_mode = GenerationMode.CONTRASTIVE_SEARCH
                else:
                    generation_mode = GenerationMode.GREEDY_SEARCH
            else:
                generation_mode = GenerationMode.SAMPLE
        else:
            if generation_config.num_beam_groups > 1:
                generation_mode = GenerationMode.GROUP_BEAM_SEARCH
            elif generation_config.do_sample is True:
                generation_mode = GenerationMode.BEAM_SAMPLE
            else:
                generation_mode = GenerationMode.BEAM_SEARCH
        return generation_mode

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

        generated_ids = self.model.generate(
            inputs,
            logits_processor=self.logit_processors,
            **self.gen_args
        )
        completion = self.tokenizer.decode(
            generated_ids[0][input_ids_cutoff:len(generated_ids[0])], 
            skip_special_tokens=True)

        # Total tokens generated
        self.total_tokens = len(generated_ids[0])-input_ids_cutoff+1

        return [completion]


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
        extra_stop_word = "\n\n"
        
        if self.mode == "original": 
            # only filter with stop-word for original mode
            completion = filter_code(raw_completion, extra_stop_word=extra_stop_word)
        else:
            # When the grammar_decoder is used
            function_incomplete = [False for _ in range(batch_size)]
            completion = self.compute_backup_completion(grammar_decoder, function_incomplete, i, input_ids_cutoff, generated_ids)

            if function_incomplete[i]:
                # if the function is incomplete, then we need to add a closing brace
                completion += "}"

        return completion

    def compute_backup_completion(self, grammar_decoder, function_incomplete, i, input_ids_cutoff, generated_ids):
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
    
    def tokenize(self, s: str) -> 'Iterable[int]':
        return self.tokenizer.encode(s, add_special_tokens=False)
