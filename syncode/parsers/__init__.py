import os
from parsers import incremental_parser
from parsers.python_parser import PythonIncrementalParser, PythonIndenter
from parsers.go_parser import GoIncrementalParser
import common
from larkm.lark import Lark
from parsers.grammars.grammar import Grammar

def create_parser(grammar: Grammar, parser='lalr', **kwargs):   
        """ 
        Creates an incremental parser for the given grammar. The parser is cached for future use.
        parser (str, optional): The type of parser to use. Can be 'lalr' or 'lr'. Defaults to 'lalr'.        
        """
        indenter = None
        parser_cache_dir = common.SYNCODE_CACHE + 'parsers/'
        cache_filename = parser_cache_dir + f'{grammar}_{parser}_parser.pkl'
        os.makedirs(os.path.dirname(parser_cache_dir), exist_ok=True)

        if grammar.name == 'python':
            indenter = PythonIndenter()

        base_parser = Lark( # This is the standard Lark parser
                        grammar.ebnf,
                        parser=parser,
                        lexer="basic",
                        start="start",
                        postlex=indenter,
                        propagate_positions=True,
                        cache = cache_filename
                    )

        if grammar.name == 'python':
            return PythonIncrementalParser(base_parser, indenter, **kwargs)
        elif grammar.name == 'go':
            return GoIncrementalParser(base_parser, **kwargs)

        return incremental_parser.IncrementalParser(base_parser, **kwargs)
