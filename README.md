# LLM-CFG

[![Test Status][test-img]][tests]
> [!WARNING]  
> This repository is currently under active development!
> 
## About
llm-cfg is a novel framework designed for the efficient and general syntactical decoding of code using Large Language Models (LLMs). The tool capitalizes on the grammar of a programming language, incorporating an offline-constructed, efficient lookup table known as a DFA mask store based on language grammar terminals.

<img width="750" alt="Screenshot 2024-01-19 at 4 40 07 PM" src="https://github.com/shubhamugare/llm-cfg/assets/14147610/9298791e-c92d-4c86-81cc-7523517def3d">



## Install and Run

Check out and install mxeval:
```
git clone https://github.com/amazon-science/mxeval.git
pip install -e mxeval
```

To run the tool, use the following command:
```
python3 syncode/infer.py
    --mode [original, grammar_mask]
    --model [model_name]
    --quantize [True, False]
    --gpu [0, 1, 2, 3]
    --num_samples [num_samples]
    --dataset [mbxp, humaneval, mathqa-x, input]
    --new_mask_store [True, False]
    --few_shot [True, False]
    --num_examples [num_examples]
    --parse_prompt [True, False]
    --dev_mode [True, False]
    --log_level [0, 1, 2]
```

### Inference Options:

- `mode` (str, optional): Mode for inference. Defaults to "original". "grammar_mask" is the mode that enables our tool.
  
- `model` (str): Model ID for Hugging Face model hub or model name if stored locally.
  
- `quantize` (bool, optional): Quantize model. Defaults to True.
  
- `gpu` (int, optional): GPU number. Defaults to 1.
  
- `num_samples` (int, optional): Number of samples. Defaults to 1.
  
- `dataset` (str, optional): Dataset. Defaults to "input". "input" indicates that the user can provide input in CLI. 
  
- `new_mask_store` (bool, optional): Forces to use a new mask store otherwise use a cached mask store if available. Defaults to False.
  
- `few_shot` (bool, optional): Run few-shot prompting. Defaults to False.
  
- `num_examples` (int, optional): Number of examples for few shot prompting. Defaults to -1.
  
- `parse_prompt` (bool, optional): If False we parse (only output) instead of (prompt+output). Defaults to True. 
  
- `dev_mode` (bool, optional): Development mode where we do not fail silently with parser errors. Defaults to False.
  
- `log_level` 0 for no logs, 1 for minimal logs, 2 for all logs including time. Defaults to 2.


The generation results are stored in a JSON file in the "results" directory. To evaluate the result of generation, use the following command:
```
python3 syncode/evaluation.py path_to_json_file
```

List of Currently Tested Models:
```
Llama models: "Llama-7b", "CodeLlama-7b", "CodeLlama-7b-Python", "Llama-13b"
CodeGen models: "Salesforce/codegen-350M-multi", "Salesforce/codegen2-1b"
Bigcode models: "bigcode/starcoderbase-1b", "bigcode/santacoder" (1.1b WIP)
WizardLM models: "WizardLM/WizardCoder-1B-V1.0"
```

[test-img]: https://github.com/shubhamugare/llm-cfg/actions/workflows/run_tests.yml/badge.svg
[tests]: https://github.com/shubhamugare/llm-cfg/actions/workflows/run_tests.yml
