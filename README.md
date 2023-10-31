# LLM-CFG

[![Test Status][test-img]][tests]

> [!WARNING]  
> This repository is currently under active development!

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
