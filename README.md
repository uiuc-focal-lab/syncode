


<p align="center">
  <img width="400" alt="syncode" src="https://github.com/shubhamugare/syncode/assets/14147610/99c30a9d-b5f5-49ab-9295-33738fde1de2" />
</p>

# SynCode: grammar augmented LLM generation [![Test Status][test-img]][tests]

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
* **SynCode** is a novel framework for grammar-guided generation of Large Language Models (LLMs) that is scalable to general-purpose programming languages and has soundness and completeness guarantees. 
* With **SynCode**, you can provably ensure that your Language Model is generating output that is syntactically valid with respect to the rules defined by a Context-Free Grammar (CFG). 


### How Does **SynCode** Compare to Other Constrained Decoders?

| Tool        | Regex     | CFG*       | Pre-Computed* | GPL* |
|-------------|-----------|-----------|:-------------:|------|
| LMQL        | ✅        | ❌        |       ❌       | ❌   |
| GUIDANCE    | ✅        | ✅        |       ❌       | ❌   |
| OUTLINES    | ✅        | ✅        |       ✅       | ❌   |
| PICARD      | ✅        | ✅        |       ❌       | ❌   |
| SYNCHROMESH | ✅        | ✅        |       ❌       | ❌   |
| LLAMA.CPP   | ✅        | ✅        |       ❌       | ❌   |
| GCD         | ✅        | ✅        |       ❌       | ❌   |
| **SynCode** | **✅**    | **✅**    |   **✅**       | **✅** |
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

<img width="750" alt="Screenshot 2024-01-19 at 4 40 07 PM" src="https://github.com/shubhamugare/llm-cfg/assets/14147610/9298791e-c92d-4c86-81cc-7523517def3d">

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
When guided with the JSON grammar with SynCode, the model is able to generate a syntactically valid JSON object. 
``` python
from syncode import Syncode

# Load the Syncode augmented model
syn_llm = Syncode(model = "microsoft/phi-2", mode='grammar_mask', grammar='json', parse_output_only=True, max_new_tokens=50)

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

Check more examples of using Python, Go, and other grammars in <a href="#-example-usage">Example Usage</a>

### SynCode Arguments
<details>
  <summary>Click to Expand on the List of Arguments for SynCode</summary>
  
- `mode` (str, optional): Mode for inference. Defaults to "original". "grammar_mask" is the mode that enables our tool.
  
- `model` (str): Model ID for Hugging Face model hub or model name if stored locally.
  
- `quantize` (bool, optional): Quantize model. Defaults to True.
  
- `device` (str, optional): Device to run the model on. Defaults to "cuda". 

- `grammar` (str, optional): Grammar in EBNF form (string or file path) or language for constrained generation. Defaults to None. You can use one of the `python`, `go`, `sql`, `json`, `calc` or pass in a custom grammar in EBNF format.
  
- `num_samples` (int, optional): Number of samples. Defaults to 1.
  
- `dataset` (str, optional): Dataset. Defaults to "input". "input" indicates that the user can provide input via CLI or by passing in a prompt as a string. 
   
- `num_few_shot` (int, optional): Number of examples for few shot prompting. Defaults to 0.
    
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
    --mode [original, grammar_mask]
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

SynCode can fix this problem! We simply switch the mode to `grammar_mask` to load the SynCode augmented model. With the constrained decoding of SynCode, the LLM is able to generate a correct Python program.  

``` python
from syncode import Syncode

model_name = "WizardLM/WizardCoder-1B-V1.0"

# Load the Syncode augmented model
syn_llm = Syncode(model=model_name, mode='grammar_mask', grammar='python')
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
syn_llm = Syncode(model = "microsoft/phi-2", mode='grammar_mask', grammar='json', parse_output_only=True, max_new_tokens=50)

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
llm = Syncode(model=model_name, mode='original', max_new_tokens=20, chat_mode=True)

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
syn_llm = Syncode(model=model_name, mode='grammar_mask', grammar=grammar, chat_mode=True)

inp = "When is the christmas day?"

output = syn_llm.infer(inp)
print(f"Syncode augmented LLM output:\n{output}")
# Syncode augmented LLM output:
# December 25 
```
&nbsp;

## 🤔 FAQs
<details><summary> Evaluation for code generation </summary>
<p>

The generation results are stored in a JSON file in the "results" directory. To evaluate the result of generation, use the following command:
```
python3 syncode/evaluation.py path_to_json_file
```
</p>
</details>

<details><summary> List of currently tested models </summary>
<p>


```
Llama models: "Llama-7b", "CodeLlama-7b", "CodeLlama-7b-Python", "Llama-13b"
CodeGen models: "Salesforce/codegen-350M-multi", "Salesforce/codegen2-1b"
Bigcode models: "bigcode/starcoderbase-1b", "bigcode/santacoder" (1.1b WIP)
WizardLM models: "WizardLM/WizardCoder-1B-V1.0"
```
</p>
</details>


<details><summary> Which parser should I use? </summary>
<p>
  
For parser selection, we offer the choice between LR(1) and LALR(1) parsers, specified by setting the parser argument to either 'lr' or 'lalr', respectively. We recommend utilizing the LR(1) parser due to its faster inference time. While constructing an LR(1) parser may require a slightly longer initial setup, we cache the parser for subsequent uses, mitigating this overhead.
</p>
</details>

[test-img]: https://github.com/shubhamugare/llm-cfg/actions/workflows/run_tests.yml/badge.svg
[tests]: https://github.com/shubhamugare/llm-cfg/actions/workflows/run_tests.yml

## Citation

```
@misc{ugare2024improving,
      title={Improving LLM Code Generation with Grammar Augmentation}, 
      author={Shubham Ugare and Tarun Suresh and Hangoo Kang and Sasa Misailovic and Gagandeep Singh},
      year={2024},
      eprint={2403.01632},
      archivePrefix={arXiv},
      primaryClass={cs.LG}
}
```

## Contact
For questions, please contact [Shubham Ugare](mailto:shubhamdugare@gmail.com).

