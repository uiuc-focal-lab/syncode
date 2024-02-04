from infer import Syncode

prompt = "Hello how are you?"
sg = Syncode(model='Salesforce/codegen-350M-multi', mode='grammar_mask', grammar="abc.lark") # grammar_mask should be default

output = sg.infer(prompt)
print(output)

result = sg.infer(dataset = 'humaneval')
print(result)
