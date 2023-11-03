from incremental_parser import IncrementalParser


class GoIncrementalParser(IncrementalParser):
    """
    This class implements an incremental parser for Python code.
    """

    def __init__(self):
        super().__init__("llm_cfg/grammars/go_grammar.lark")
