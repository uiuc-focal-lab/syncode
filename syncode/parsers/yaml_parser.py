
from contextvars import Token
from typing import Iterator

import regex
from syncode.larkm.indenter import Indenter


class YamlIndenter(Indenter):
        """
        This class implements the indenter for yaml code.
        """
        NL_type = "_NL"
        INDENT_type = "_INDENT"
        DEDENT_type = "_DEDENT"
        CLOSE_PAREN_types, OPEN_PAREN_types, tab_len = [], [], 1
