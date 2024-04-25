import sys, os
sys.path.append(os.getcwd() + '/../')

from syncode import Syncode
import warnings

warnings.filterwarnings('ignore')

model_name = "microsoft/phi-2"

# Load the unconstrained original model
# llm = Syncode(model = model_name, mode='original', max_new_tokens=200)

# Load the Syncode augmented model
syn_llm = Syncode(model = model_name, mode='grammar_mask', grammar='java', parse_output_only=True)

prompt = "Write HelloWorld.java, which prints Hello World!\n"
# llm_output = llm.infer(prompt)[0]
# print(f"LLM output:\n{llm_output}\n")

syn_llm_output = syn_llm.infer(prompt)[0]
print(f"Syncode augmented LLM output:\n{syn_llm_output}")