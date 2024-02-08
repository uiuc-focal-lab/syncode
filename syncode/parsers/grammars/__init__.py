import os
import incremental_parser
from syncode.parsers.python_parser import PythonIncrementalParser
from syncode.parsers.go_parser import GoIncrementalParser
import common
from larkm.indenter import PythonIndenter
from larkm.lark import Lark

def create_parser(grammar, parser='lalr', **kwargs):   
        """ 
        Creates an incremental parser for the given grammar.
        """
        grammar_file = f'syncode/grammars/{grammar}_grammar.lark'
        indenter = None

        parser_cache_dir = common.SYNCODE_CACHE + 'parsers/'
        cache_filename = parser_cache_dir + f'{grammar}_{parser}_parser.pkl'
        os.makedirs(os.path.dirname(parser_cache_dir), exist_ok=True)

        grammar_filename =  f'syncode/grammars/{grammar}_grammar.lark'
        if grammar == 'python':
            indenter = PythonIndenter()
        elif not os.path.exists(grammar_filename):
            # In this case we assume that the user provides the full path to the grammar file
            grammar_filename = grammar

        # Initialize the parser
        if os.path.exists(grammar_filename):
            with open(grammar_filename, 'r') as file:
                grammar_file = file.read()
        else:
            # Grammar can also be specified as a string in EBNF form
            # TODO: validate this
            grammar_file = grammar_filename  

        base_parser = Lark( # This is the standard Lark parser
                        grammar_file,
                        parser=parser,
                        lexer="basic",
                        start="start",
                        postlex=indenter,
                        propagate_positions=True,
                        cache = cache_filename
                    )

        if grammar == 'python':
            return PythonIncrementalParser(base_parser, **kwargs)
        elif grammar == 'go':
            return GoIncrementalParser(base_parser, **kwargs)
        elif os.path.exists(grammar):
            if grammar.endswith('.lark'):
                return incremental_parser.IncrementalParser(base_parser, **kwargs)
            else:
                 raise ValueError('grammar input file must have .lark extension')

        # Grammar can also be specified as a string in EBNF form
        # TODO: validate this
        return incremental_parser.IncrementalParser(base_parser, **kwargs)
