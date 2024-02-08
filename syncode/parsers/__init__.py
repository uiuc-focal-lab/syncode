import os
from parsers import incremental_parser
from parsers.python_parser import PythonIncrementalParser, PythonIndenter
from parsers.go_parser import GoIncrementalParser
import common
from larkm.lark import Lark

def create_parser(grammar, parser='lalr', **kwargs):   
        """ 
        Creates an incremental parser for the given grammar.
        """
        indenter = None
        parser_cache_dir = common.SYNCODE_CACHE + 'parsers/'
        cache_filename = parser_cache_dir + f'{grammar}_{parser}_parser.pkl'
        os.makedirs(os.path.dirname(parser_cache_dir), exist_ok=True)
        grammar_filename = None

        if grammar == 'python':
            indenter = PythonIndenter()
            grammar_filename =  f'syncode/parsers/grammars/{grammar}_grammar.lark'
        elif grammar in ['go', 'tiny', 'calc']:
            grammar_filename = f'syncode/parsers/grammars/{grammar}_grammar.lark'
        elif grammar.endswith('.lark'): 
            if os.path.exists(grammar):
                # In this case we assume that the user provides the full path to the grammar file
                grammar_filename = grammar
            else:
                raise ValueError(f'grammar input file {grammar} does not exist!')            
    
        if grammar_filename is not None:
            if os.path.exists(grammar):
                    with open(grammar_filename, 'r') as file:
                        grammar_def = file.read()
        else: # Grammar can also be specified as a string in EBNF form
            grammar_def = grammar

        base_parser = Lark( # This is the standard Lark parser
                        grammar_def,
                        parser=parser,
                        lexer="basic",
                        start="start",
                        postlex=indenter,
                        propagate_positions=True,
                        cache = cache_filename
                    )

        if grammar == 'python':
            return PythonIncrementalParser(base_parser, indenter, **kwargs)
        elif grammar == 'go':
            return GoIncrementalParser(base_parser, **kwargs)

        return incremental_parser.IncrementalParser(base_parser, **kwargs)
