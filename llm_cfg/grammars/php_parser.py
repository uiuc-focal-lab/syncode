import time
import lark
from incremental_parser import IncrementalParser
from parse_result import ParseResult


class PhpIncrementalParser(IncrementalParser):
    """
    This class implements an incremental parser for PHP code.
    """

    def __init__(self):
        super().__init__("llm_cfg/grammars/php_grammar.lark")
