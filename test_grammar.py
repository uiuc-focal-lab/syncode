from lark import Lark
from lark.indenter import Indenter

class PythonIndenter(Indenter):
    NL_type = "_NL"
    OPEN_PAREN_types = ["LPAR", "LSQB", "LBRACE"]
    CLOSE_PAREN_types = ["RPAR", "RSQB", "RBRACE"]
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    tab_len = 4

parser = Lark.open(
    "python_grammar.lark",
    parser="lalr",
    start="file_input",
    postlex=PythonIndenter(),
    propagate_positions=True,
)

code = f"""
def dummy(a, b):
    ""\" Whatever man!
    ""\"
    a = 3
    b = 5
    return a + b
"""

code = f"""
a = 3
b = 4
c = 5

def f():
      ""\"
      funcdef!!!
      ""\"
      a = 4
      c = 3
    
      # Random comment
      if i == 2:
        2 + 3
        t + 1
        pass
      else:
        return
      
      return sss
"""

print(code)
interactive = parser.parse_interactive(code)

print(parser.parse(code))