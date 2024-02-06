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
parsers = ['lalr', 'lr']


for model, grammar, dataset, mode in zip(models, grammars, datasets, modes):
    if mode == 'original':
        parsers = [None]
    else:
        parsers = ['lalr', 'lr']

    for parser in parsers: 
        compile_and_run(
            model, 
            mode=mode, 
            gpu=1, 
            num_samples=1, 
            grammar=grammar, 
            dataset=dataset, 
            few_shot=False, 
            log_level=1, 
            new_mask_store=False, 
            parser=parser)
