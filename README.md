


<p align="center">
  <img width="400" alt="syncode" src="https://github.com/shubhamugare/syncode/assets/14147610/99c30a9d-b5f5-49ab-9295-33738fde1de2" />
</p>

# SynCode: LLM Generation with Grammar Augmentation [![Test Status][test-img]][tests]

<p align="left">
    ℹ️&nbsp;<a href="#-about">About</a>
    | 📚&nbsp;<a href="#-features">Features</a>
    | 📖&nbsp;<a href="#-more-about-syncode">More About SynCode</a>
    | 🚀&nbsp;<a href="#-quick-start">Quick Start</a>
    | 👀&nbsp;<a href="#-example-usage">Example Usage</a>
    | 🤔&nbsp;<a href="#-faq">FAQs</a>
</p>

> [!WARNING]  
> This repository is currently under active development!

## ℹ️ About
* **SynCode** is a novel framework for the grammar-guided generation of Large Language Models (LLMs) that is scalable to general-purpose programming languages and has soundness and completeness guarantees. 
* With **SynCode**, you can ensure that your Language Model is generating output that is syntactically valid with respect to the rules defined by a Context-Free Grammar (CFG). 

## Builtin Grammars

![Python](https://img.shields.io/badge/Python-Supported-blue.svg)  ![Go](https://img.shields.io/badge/Go-Supported-00ADD8.svg)  ![SQL](https://img.shields.io/badge/SQL-Supported-orange.svg)  ![JSON](https://img.shields.io/badge/JSON-Supported-lightgrey.svg) 

![Misc](https://img.shields.io/badge/Miscellaneous-Supported-purple.svg) Define your own grammar using simple EBNF syntax. Check out our [notebooks directory](./notebooks/) for examples


## How Does **SynCode** Compare to Other Constrained Decoders?


| Tool                                                      | Regex     | CFG*       | Pre-Computed* | GPL* |
|----------------------------------------------------       |-----------|-----------|:-------------:|------|
| [`LMQL`](https://github.com/eth-sri/lmql)                 | ✅        | ❌        |       ❌       | ❌   |
| [`GUIDANCE`](https://github.com/guidance-ai/guidance)     | ✅        | ✅        |       ❌       | ❌   |
| [`OUTLINES`](https://github.com/outlines-dev/outlines)    | ✅        | ✅        |       ✅       | ❌   |
| [`PICARD`](https://github.com/ServiceNow/picard)          | ✅        | ✅        |       ❌       | ❌   |
| [`SYNCHROMESH`](https://arxiv.org/abs/2201.11227)         | ✅        | ✅        |       ❌       | ❌   |
| [`LLAMA.CPP`](https://github.com/ggerganov/llama.cpp)     | ✅        | ✅        |       ❌       | ❌   |
| [`GCD`](https://arxiv.org/abs/2305.13971)                 | ✅        | ✅        |       ❌       | ❌   |
| **SynCode**                                               | **✅**    | **✅**    |   **✅**       | **✅** |
---

**CFG***: Guide generation with a Context Free Grammar (CFG)

**Pre-Computed***: Precompute masks over the vocabulary to significantly improve generation speed

**GPL***: Support general-purpose programming languages, which involve non-context-free fragments, such as  indentation in Python and end-of-scope markers in Golang.


## 📚 Features
|                                                                                                              |
|---------------------------------------------------------------------------------------------------------------------|
| 🔥 Fast grammar-guided generation (as little as 10% generation overhead with Python and Go!)                        |
| 🤖 Seamlessly work with any HuggingFace Language Model, including Code, Chat, and Instruct models                   |
| 🖍️ Pass in any CFG in the EBNF format (even large grammars for programming languages like Python and Go!)            |
| 📝 Built-in CFGs for **Python, Go, SQL, Math, JSON**, and more!                                                              |
| 🎲 Sample with any existing decoding strategy (eg. greedy, beam search, nucleus sampling)                           |


## 📖 More About **SynCode**

### How **SynCode** works?

<img width="750" alt="Screenshot 2024-03-21 at 2 22 15 AM" src="https://github.com/uiuc-focal-lab/syncode/assets/14147610/d9d73072-3c9b-47d4-a941-69d5cf8fb1bf">

The backbone of SynCode is the offline construction of a DFA mask store, a lookup table derived from regular expressions representing the terminals of the language grammar. The DFA mask store facilitates efficient traversal of DFA states, enabling the retrieval of masks mapped to each state and accept sequence. In the SynCode workflow, the LLM takes partial code _C<sub>k</sub>_ and generates a distribution for the next token _t<sub>k+1</sub>_. The incremental parser processes _C<sub>k</sub>_ to generate accept sequences _A_, the sequences of terminals that can follow partial code called accept sequences. Simultaneously, the incremental parser computes a remainder _r_ from the partial code, representing the suffix that may change its terminal type in subsequent generations. SynCode walks over the DFA using the remainder and uses the mask store to compute the mask specific to each accept sequence. By unifying masks for each accept sequence SynCode gets the set of syntactically valid tokens. The LLM iteratively generates a token _t<sub>k+1</sub>_ using the distribution and the mask, appending it to _C<sub>k</sub>_ to create the updated code _C<sub>k+1</sub>_. The process continues until the LLM returns the final code _C<sub>n</sub>_ based on the defined stop condition.

## 🚀 Quick Start
### Python Installation and Usage Instructions
Simply install SynCode via PyPi using the following command:
``` bash
pip install git+https://github.com/uiuc-focal-lab/syncode.git
```
Then, in your Python program,
``` python
from syncode import Syncode
```
Refer to <a href="###-syncode-arguments">SynCode Arguments</a> for the full list of arguments to initialize the __SynCode__ class. 
In Python, inference is performed using the __infer()__ method in the __SynCode__ class. __infer()__ has the following arguments:
- `prompt` (str, optional): Prompt to the Language Model. Defaults to None.
  
- `task_id` (int, optional): Problem task id for selecting a problem from a Dataset. Defaults to None.

If both `prompt` and `task_id` are not specified, __infer()__ reads user input via `stdin`. 

The following example shows the benefit of SynCode:

In the example below, the unconstrained original Phi-2 model fails to generate a valid JSON object and instead generates Python code.
``` python
from syncode import Syncode

# Load the unconstrained original model
llm = Syncode(model = "microsoft/phi-2", mode='original', max_new_tokens=50)

prompt = "Please return a json object to represent country India with name, capital and population?"
output = llm.infer(prompt)[0]
print(f"LLM output:\n{output}\n")

# LLM output:
#
# A:
#
# You can use the following code:
# import json
#
# def get_country_info(country_name):
#    country_info = {
#        'name': country_name,
#        'capital':
```
When guided with the JSON grammar with SynCode, the model can generate a syntactically valid JSON object. 
``` python
from syncode import Syncode

# Load the Syncode augmented model
syn_llm = Syncode(model = "microsoft/phi-2", grammar='json', parse_output_only=True, max_new_tokens=50)

prompt = "Please return a json object to represent country India with name, capital and population?"
output = syn_llm.infer(prompt)[0]
print(f"SynCode output:\n{output}")

# SynCode output:
# {
#     "name": "India",
#     "capital": "New Delhi",
#     "population": "1,366,417,754"
# }
```

Check more examples of using Python, Go, and other grammars in <a href="#-example-usage">Notebooks</a> and a quick example at 
&nbsp; [<img align="center" src="https://colab.research.google.com/assets/colab-badge.svg" />](https://colab.research.google.com/github/stanfordnlp/dspy/blob/main/intro.ipynb)

### SynCode Arguments
<details>
  <summary>Click to Expand on the List of Arguments for SynCode</summary>
  
- `mode` (str, optional): Mode for inference. `grammar_mask` and `grammar_strict` are the modes that enable our tool. `original` is the mode for the original LLM. Defaults to "grammar_strict". "original" mode is used for the original LLM without any grammar constraints and "grammar_strict" mode is a stricter mode for grammar-constrained generation.
  
- `model` (str): Model ID for Hugging Face model hub or model name if stored locally.
  
- `quantize` (bool, optional): Quantize the model to bfloat16. Defaults to True.
  
- `device` (str, optional): Device to run the model on. Defaults to "cuda". 

- `grammar` (str, optional): Grammar in EBNF form (string or file path) or language for constrained generation. Defaults to None. You can use one of the `python`, `go`, `sql`, `json`, `java`, `calc` or pass in a custom grammar (check notebooks for examples) in EBNF format.
  
- `num_samples` (int, optional): Number of samples. Defaults to 1.
  
- `dataset` (str, optional): Dataset. Defaults to "input". "input" indicates that the user can provide input via CLI or by passing in a prompt as a string. 
   
- `num_few_shot` (int, optional): Number of examples for few-shot prompting. Defaults to 0.
    
- `chat_mode` (bool, optional): True if using a Chat/Instruct LLM. False otherwise. Defaults to False. 
  
- `dev_mode` (bool, optional): Development mode where we do not fail silently with parser errors. Defaults to False.
  
- `log_level` (int, optional): 0 for no logs, 1 for minimal logs, 2 for all logs including time. Defaults to 2.

- `new_mask_store` (bool, optional): Forces to use a new mask store otherwise use a cached mask store if available. Defaults to False.

- `parser` (str, optional): Choose between LR(1) and LALR(1) parsing. Defaults to 'lalr'.

- `task_id` (int, optional): Problem task id for selecting a problem from a Dataset.

- `kwargs`(void, optional): Currently supported `kwargs` are `max_length`, `max_new_tokens`, `min_length`, `min_new_tokens`, `early_stopping`, `do_sample`, `num_beams`, `use_cache`, `temperature`, `top_k`, `top_p`, `num_return_sequences`, `pad_token_id`, and `eos_token_id`. Refer to the [HuggingFace Text Generation Documentation](https://huggingface.co/docs/transformers/en/main_classes/text_generation) for more information.

  
</details>

### Running with CLI
<details>
  <summary>Running SynCode via CLI</summary>

Clone this repository:
```
git clone https://github.com/uiuc-focal-lab/syncode.git
```

To run the tool with CLI, use the following command:
```
python3 syncode/infer.py
    --mode [original, grammar_mask, grammar_strict]
    --model [model_name]
    --quantize [True, False]
    --device ["cpu", "cuda", "cuda:1" etc.]
    --num_samples [num_samples]
    --dataset [mbxp, humaneval, mathqa-x, input]
    --few_shot [True, False]
    --num_fs_examples [num_fs_examples]
    --chat_mode [True, False]
    --dev_mode [True, False]
    --log_level [0, 1, 2]
    --new_mask_store [True, False]
    --parser ["lr", "lalr"]
    --task_id [task_id]
```
</details>

### Environment Variables
Optionally, you can set the directories for cache by exporting the following environment variables. Add the following lines to your .bashrc or .zshrc file:
```
export HF_CACHE="path_to_hf_cache"
export SYNCODE_CACHE="path_to_syncode_cache"
```
If these environment variables are not set, the tool will use the default cache directories.


## 👀 Example Usage
Check out our [notebooks directory](./notebooks/) which contains various interactive examples that showcase different use cases of **SynCode**! The grammars for some common programming languages are defined in the [grammars directory](./syncode/parsers/grammars/). We also allow users to define a grammar using a simple EBNF syntax adapted from Lark. Users can pass in a string of rules or a path to a .lark file. 

### 🐍 Generate Indentation-Error-Free Python Code 

Large Language Models tend to struggle with generating Python code with correct indentation. Consider the example below. The unconstrained `original` WizardCoder model fails to generate a code completion with the correct number of spaces. When executing this code, we get an Indentation Error. 

``` python
from syncode import Syncode

model_name = "WizardLM/WizardCoder-1B-V1.0"

# Load the unconstrained original model
llm = Syncode(model = model_name, mode='original', max_new_tokens=200)
partial_code = "def is_prime(n):\n    '''Return if prime'''\n  "

#generate a completion to the input partial code
unconstrained_output = partial_code+llm.infer(partial_code)[0]

print(unconstrained_output)
# def is_prime(n):
#     '''Return if prime'''
#    if n < 2:
#        return False
#    for i in range(2, int(n**0.5)+1):
#        if n % i == 0:
#            return False
#    return True
exec(unconstrained_output)
# IndentationError: unindent does not match any outer indentation level
```

SynCode can fix this problem! We simply switch the mode to `grammar_mask`/`grammar_strict` to load the SynCode augmented model. With the constrained decoding of SynCode, the LLM is able to generate a correct Python program.  

``` python
from syncode import Syncode

model_name = "WizardLM/WizardCoder-1B-V1.0"

# Load the Syncode augmented model
syn_llm = Syncode(model=model_name, mode='grammar_strict', grammar='python')
partial_code = "def is_prime(n):\n    '''Return if prime'''\n  "

#generate a completion to the input partial code
constrained_output = partial_code+ syn_llm.infer(partial_code)[0]
print(constrained_output)
# def is_prime(n):
#     '''Return if prime'''
#     if n < 2:
#         return False
#     for i in range(2, int(n**0.5) + 1):
#         if n % i == 0:
#             return False
#     return True
exec(constrained_output)
# Correct Code :)
```
### 🔤 JSON Mode Generation
In the example below, the unconstrained original Phi-2 model fails to generate a valid JSON object and instead generates Python code.
``` python
from syncode import Syncode

# Load the unconstrained original model
llm = Syncode(model = "microsoft/phi-2", mode='original', max_new_tokens=50)

prompt = "Please return a json object to represent country India with name, capital and population?"
output = llm.infer(prompt)[0]
print(f"LLM output:\n{output}\n")

# LLM output:
#
# A:
#
# You can use the following code:
# import json
#
# def get_country_info(country_name):
#    country_info = {
#        'name': country_name,
#        'capital':
```
When guided with the JSON grammar with SynCode, the model is able to generate a syntactically valid JSON object. 
``` python
from syncode import Syncode

# Load the Syncode augmented model
syn_llm = Syncode(model="microsoft/phi-2", grammar='json', parse_output_only=True, max_new_tokens=50)

prompt = "Please return a json object to represent country India with name, capital and population?"
output = syn_llm.infer(prompt)[0]
print(f"SynCode output:\n{output}")

# SynCode output:
# {
#     "name": "India",
#     "capital": "New Delhi",
#     "population": "1,366,417,754"
# }
```
### 👤 Custom Grammar Input 
Syncode allows user to define a grammar using a simple EBNF syntax adapted from Lark. One can also simply feed the grammar rules directly as a string of rules as shown below. In our example, we want our model to only respond in the format `month day`. Without constrained decoding, the Language Model may not generate output that follows this syntax. Consider the code snippet below. 

``` python
from syncode import Syncode

model_name = "microsoft/phi-2"

# Load the unconstrained original model
llm = Syncode(model=model_name, mode='original', max_new_tokens=20)

inp = "When is the christmas day?"

output = llm.infer(inp)
print(f"LLM output:\n{repr(output)}\n")
# LLM output:
# 'Christmas Day is on December 25th.\n<|im_end|>\n<|im'
```

As shown above, the LLM generates a correct response but not in the format we want. We can pass in a grammar and leverage the ability of SynCode to guide the LLM generation with this grammar. As shown in the snippet below, the SynCode augmented LLM generates output in the correct `month day` format.

``` python
from syncode import Syncode

# Pass in a grammar as a string of rules in EBNF format
grammar = """ start: month day 
              
              day: /[1-9]/ | /[1-2][0-9]/ | /3[0-1]/
              
              month: "January" | "February" | "March" | "April" | "May" | "June" | "July" | "August" | "September" | "October" | "November" | "December"
"""

model_name = "microsoft/phi-2"

# Load the Syncode augmented model
syn_llm = Syncode(model=model_name, grammar=grammar, parse_output_only=True)

inp = "When is the christmas day?"

output = syn_llm.infer(inp)
print(f"Syncode augmented LLM output:\n{output}")
# Syncode augmented LLM output:
# December 25 
```
&nbsp;

## 🤔 FAQs
<details><summary> Which parser should I use? </summary>
<p>
  
For parser selection, we offer the choice between LR(1) and LALR(1) parsers, specified by setting the parser argument to either 'lr' or 'lalr', respectively. We recommend utilizing the LR(1) parser due to its faster inference time. While constructing an LR(1) parser may require a slightly longer initial setup, we cache the parser for subsequent uses, mitigating this overhead.
</p>
</details>

<details><summary> What is the difference between `grammar_mask` and `grammar_strict` modes? </summary>

<p>
  
We have recently added `grammar_strict` mode which works better for some grammars that are not well-known to the LLM from its training/fine-tuning. Please refer to this [`Notebook`](https://github.com/uiuc-focal-lab/syncode/blob/main/notebooks/example_misc.ipynb) for examples where `grammar_strict` mode does much better than `grammar_mask` mode. 
  
There are two main differences between these modes:
  
1. grammar_mask mode aims for overapproximation in allowing tokens. For example, if the sequence to accept is [NAME, LPAR] and the current input is "print", grammar_mask will permit anything that starts with '(', such as '(', '()', or '(['. This mode ensures no grammatical generation possibility is excluded.
grammar_strict mode, conversely, would only allow '(' in this scenario. It does not overapproximate, meaning it adheres strictly to the immediate grammatical requirements.


2. grammar_mask mode allows all special tokens at any time, including the EOS (End Of Sequence) token, allowing the generation to conclude whenever.
grammar_strict mode only permits the EOS token when the generation is a valid grammatical completion, specifically when $END is in the accept sequence.
</p>
</details>

[test-img]: https://github.com/shubhamugare/llm-cfg/actions/workflows/run_tests.yml/badge.svg
[tests]: https://github.com/shubhamugare/llm-cfg/actions/workflows/run_tests.yml

## 📜 Citation
<p>
    <a href="https://arxiv.org/abs/2403.01632"><img src="https://img.shields.io/badge/Paper-arXiv-blue"></a>
</p>

```
@misc{ugare2024syncode,
      title={SynCode: LLM Generation with Grammar Augmentation}, 
      author={Shubham Ugare and Tarun Suresh and Hangoo Kang and Sasa Misailovic and Gagandeep Singh},
      year={2024},
      eprint={2403.01632},
      archivePrefix={arXiv},
      primaryClass={cs.LG}
}
```

## Contact
For questions, please contact [Shubham Ugare](mailto:shubhamdugare@gmail.com).

