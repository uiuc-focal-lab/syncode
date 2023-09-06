from lark import Lark
from lark.indenter import Indenter

class PythonIndenter(Indenter):
    NL_type = "_NEWLINE"
    OPEN_PAREN_types = ["LPAR", "LSQB", "LBRACE"]
    CLOSE_PAREN_types = ["RPAR", "RSQB", "RBRACE"]
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    tab_len = 8

parser = Lark.open(
    "python_grammar.lark",
    parser="lalr",
    start="file_input",
    postlex=PythonIndenter(),
    propagate_positions=True,
)

interactive = parser.parse_interactive("for x")

# feeds the text given to above into the parsers. This is not done automatically.
interactive.exhaust_lexer()

# returns the names of the Terminals that are currently accepted.
print(interactive.accepts())