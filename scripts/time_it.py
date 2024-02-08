import sys, os
sys.path.append('syncode') # Assuming we are in the root directory
from infer import compile_and_run


models = ['Salesforce/codegen-350M-multi', 'WizardLM/WizardCoder-1B-V1.0', 'Llama-7b']
# models = ['WizardLM/WizardCoder-1B-V1.0']
grammars = ['python', 'go']
# grammars = ['python']
# datasets = ['mbxp', 'humaneval']
datasets = ['humaneval']
modes = ['original', 'grammar_mask']

product = [(model, dataset, mode, grammar) for model in models for dataset in datasets for mode in modes for grammar in grammars]

for model, dataset, mode, grammar in product:
    if mode == 'original':
        parsers = [None]
    else:
        parsers = ['lalr', 'lr']

    for parser in parsers: 
        print(f"Running {model} with {grammar} grammar and {dataset} dataset in {mode} mode with {parser} parser")
        compile_and_run(
            model, 
            mode=mode, 
            gpu=1, 
            num_samples=1, 
            grammar=grammar, 
            dataset=dataset, 
            few_shot=False, 
            log_level=0, 
            new_mask_store=False, 
            parser=parser)
