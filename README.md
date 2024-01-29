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
python3 llm_cfg/infer.py --mode [original, grammar_mask, synchromesh] --model_size [7B, 13B] --quantize [True, False] --gpu [0, 1, 2, 3]
```
The results of generation are stored in a json file in results directory. To evaluate the result of generation use following command
```
python3 llm_cfg/evaluation.py path_to_json_file
```

[test-img]: https://github.com/shubhamugare/llm-cfg/actions/workflows/run_tests.yml/badge.svg
[tests]: https://github.com/shubhamugare/llm-cfg/actions/workflows/run_tests.yml
