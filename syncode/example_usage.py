from infer import Syncode

# prompt = "Hello how are you?"
# grammar = """
# start: expr

# ?expr: term
#      | expr "+" term  -> add
#      | expr "-" term  -> subtract

# ?term: factor
#      | term "*" factor  -> multiply
#      | term "/" factor  -> divide

# ?factor: NUMBER        -> number
#        | "(" expr ")"

# %import common.NUMBER
# %import common.WS
# %ignore WS"""

sg = Syncode(model='Salesforce/codegen-350M-multi', mode='grammar_mask', grammar= 'python') # grammar_mask should be default

sg.infer()
# # output = sg.infer(prompt)
# # print(output)

# # result = sg.infer(dataset = 'humaneval')
# # print(result)

# sg = Syncode(model = "test", mode = 'original', device = 'cpu', do_sample = False)
# output = sg.infer("def print_hello_world():")
# print(output)
