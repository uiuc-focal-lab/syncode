
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

        #Check if user specified path to grammar exists
        if os.path.exists(grammar):
            if grammar.endswith('.lark'):
                return incremental_parser.IncrementalParser(grammar, **kwargs)
            else:
                 raise ValueError('grammar input file must have .lark extension')

        # Grammar can also be specified as a string in EBNF form
        return incremental_parser.IncrementalParser(grammar, **kwargs)
