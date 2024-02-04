
import os
import incremental_parser
from grammars.python_parser import PythonIncrementalParser
from grammars.go_parser import GoIncrementalParser


def create_parser(grammar, **kwargs):
        """ 
        Creates an incremental parser for the given grammar.
        """
        if grammar == 'python':
            return PythonIncrementalParser(**kwargs)
        elif grammar == 'go':
            return GoIncrementalParser(**kwargs)

        # Check if file "syncode/grammars/{grammar}_grammar.lark" exists
        if os.path.exists(f'syncode/grammars/{grammar}_grammar.lark'):
            return incremental_parser.IncrementalParser(f'syncode/grammars/{grammar}_grammar.lark', **kwargs)

        # If the grammar is not found, raise an error
        raise ValueError(f'Unknown grammar: {grammar}')
