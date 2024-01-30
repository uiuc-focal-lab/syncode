
import os
import incremental_parser
from grammars.python_parser import PythonIncrementalParser
from grammars.go_parser import GoIncrementalParser


def create_parser(grammar, logger=None):
        """ 
        Creates an incremental parser for the given grammar.
        """
        if grammar == 'python':
            return PythonIncrementalParser(logger=logger)
        elif grammar == 'go':
            return GoIncrementalParser(logger=logger)

        # Check if file "llm_cfg/grammars/{grammar}_grammar.lark" exists
        if os.path.exists(f'llm_cfg/grammars/{grammar}_grammar.lark'):
            return incremental_parser.IncrementalParser(f'llm_cfg/grammars/{grammar}_grammar.lark', logger=logger)

        # If the grammar is not found, raise an error
        raise ValueError(f'Unknown grammar: {grammar}')
