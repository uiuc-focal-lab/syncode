import copy
import re
from parse_result import ParseResult
from lark.lexer import Token
from lark import Lark


class IncrementalParser:
    def __init__(self, grammar_file, indenter=None) -> None:
        self.cur_ac_terminals = None
        self.next_ac_terminals = None
        self.cur_pos = 0 # Current cursor position in the lexer tokens list
        self.lexer_pos = 0 # Current lexer position in the code
        self.dedent_queue = []

        self.parser = Lark.open( # This is the standard Lark parser
            grammar_file,
            parser="lalr",
            lexer="basic",
            start="file_input",
            postlex=indenter,
            propagate_positions=True,
        )
        self.interactive = self.parser.parse_interactive('')
        self.parser_token_seq = []
        self.log_time = False

        # To enable going back to old state of the parser
        self.prev_lexer_tokens = None
        self.cur_pos_to_interactive = {}
    
    def get_acceptable_next_terminals(self, code) -> ParseResult:
        pass
    
    def _store_parser_state(self, pos, parser_state, accepts):      
        indent_levels = copy.deepcopy(self.indent_level)  
        self.cur_pos_to_interactive[pos] = (parser_state, indent_levels, accepts, copy.deepcopy(self.dedent_queue))
        self.cur_ac_terminals = copy.deepcopy(self.next_ac_terminals)
        self.next_ac_terminals = copy.deepcopy(accepts)
        # print('Storing state at position:', pos, len(self.interactive.parser_state.state_stack), len(self.dedent_queue), len(self.indent_level))

    def _restore_parser_state(self, pos):
        parser_state, indent_levels, self.cur_ac_terminals, dedent_queue = self.cur_pos_to_interactive[pos]
        self.interactive.parser_state = parser_state.copy()
        self.dedent_queue = copy.deepcopy(dedent_queue)
        self.indent_level = copy.deepcopy(indent_levels)
        # print('restoring state at position:', pos, len(self.interactive.parser_state.state_stack), len(self.dedent_queue), len(self.indent_level))
