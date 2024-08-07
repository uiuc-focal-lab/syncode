from llama_cpp import Llama, LogitsProcessorList, LlamaGrammar
from syncode import SyncodeLogitsProcessor, Grammar
from syncode.dataset import Dataset
from syncode.common import LlamaTokenizerWrapper
import unittest
import json
import torch

class TestSyncode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.llm = Llama.from_pretrained(
            repo_id="bartowski/Lite-Mistral-150M-v2-Instruct-GGUF",
            filename="Lite-Mistral-150M-v2-Instruct-Q6_K.gguf",
            verbose=False
        )
        cls.grammar = Grammar('json')
        cls.dataset = Dataset('json_eval')
    
    def test_wrapper(self):
        wrapper = LlamaTokenizerWrapper(self.llm)
        actual_tokenizer = self.llm.tokenizer_

        for i, problem in enumerate(self.dataset.problems):
            prompt = problem['prompt'][0]['content']
            wrapper_tokd = wrapper.encode(prompt)
            actual_tokd = actual_tokenizer.encode(prompt)
            assert wrapper_tokd[0] == actual_tokd, f'Encoding Error for {i}'
            
            wrapper_tokd_tensor = torch.tensor(wrapper_tokd)
            wrapper_decoded = wrapper.batch_decode(wrapper_tokd)[0]
            actual_decoded = actual_tokenizer.decode(actual_tokd)
            wrapper_tensor_decoded = wrapper.batch_decode(wrapper_tokd_tensor)[0]
            assert wrapper_decoded == actual_decoded == wrapper_tensor_decoded == prompt, f'Decoding Error for {i}'

    def test_llama_cpp(self):
        failed = []
        for i, problem in enumerate(self.dataset.problems):
            if i == 27:
                continue #skip this one due to context length of the model

            response = self.llm.create_chat_completion(
            messages= problem['prompt'], 
            max_tokens = 400, 
            logits_processor = LogitsProcessorList([SyncodeLogitsProcessor(grammar = self.grammar, 
                                                                            tokenizer = self.llm, 
                                                                            parse_output_only= True)])
            )
            try:
                json.loads(response["choices"][0]["message"]["content"])
            except:
                failed.append(i)

        assert not failed, f'Synax Error for Problems: {failed}'
        


