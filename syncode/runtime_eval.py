from infer import Syncode
import argparse

# Create the parser
p = argparse.ArgumentParser(description='select mode and model for runtime evaluation')

# Add an argument
p.add_argument('--model', default='Salesforce/codegen-350M-multi', help='The model that you are going to use')
p.add_argument('--mode', default='original', help='The mode that you are going to use')
p.add_argument('--grammar', default='python', help='The grammar that you are going to use')
p.add_argument('--parser', default='lr', help='The parser that you will use')
p.add_argument('--device', default='cuda:1', help='gpu usage')

# Parse the arguments
args = p.parse_args()

# print(args.max_new_tokens)
print(args.model)
print(args.mode)
print(args.parser)
print(args.device)
def compile_and_runtime(model, mode="original", quantize=True, device="cuda:1", num_samples=-1, grammar="python", dataset="humaneval", few_shot=False, num_examples=-1, parse_prompt=True, dev_mode=False, log_level=0, new_mask_store=False, parser="lr", task_id=None, max_new_tokens=50, **kwargs):
    sc = Syncode(model, mode=mode, quantize=quantize, device=device, num_samples=1 , grammar=grammar, dataset=dataset, few_shot=few_shot, num_fs_examples= 1 , parse_prompt=parse_prompt, dev_mode=dev_mode, log_level=log_level, new_mask_store=new_mask_store, parser=parser, task_id=task_id, max_new_tokens=max_new_tokens, **kwargs)
    # print(sc.kwargs.get('max_new_tokens'))
    sc.infer(task_id=task_id)

for i in range(50, 450, 50):
    compile_and_runtime(model=args.model, mode=args.mode, grammar=args.grammar, max_new_tokens=i, parser=args.parser)
    print(f"finished running max_new_tokens:{i}")

# compile_and_runtime(model=args.model, mode=args.mode, grammar=args.grammar, max_new_tokens=250)

        # sg = Syncode(model=args.model, mode=args.mode, grammar=args.grammar, max_new_tokens=i)

# sg = Syncode(model='Salesforce/codegen-350M-multi', mode='grammar_mask', grammar="abc.lark") # grammar_mask should be default

# compile_and_runtime(model=args.model, mode=args.mode, grammar=args.grammar, max_new_tokens=50)
# sg = Syncode(model='Salesforce/codegen-350M-multi', mode=args.mode, grammar=args.grammar, max_new_tokens=50, dataset = 'humaneval')
# sg.run_code_eval(sg.num_samples, sg.out_path)
# print(result)