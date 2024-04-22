import copy, time
import syncode.common as common
import syncode.larkm as lark
from syncode.larkm.parsers.lalr_interactive_parser import InteractiveParser
from syncode.parse_result import ParseResult, RemainderState
from syncode.larkm.lexer import Token
from typing import Optional, Any, Tuple, Iterable

class IncrementalParser:    
    """
    This is the base class for all incremental parsers.
    """
    def __init__(self, base_parser, logger: Optional[common.Logger]=None) -> None:
        self.cur_pos = 0 # Current cursor position in the lexer tokens list
        self.lexer_pos = 0 # Current lexer position in the code
        self.dedent_queue: list = []

        # Initialize the parser
        time_start = time.time()
        self.base_parser = base_parser

        self.logger = logger if logger is not None else common.EmptyLogger()
        self.logger.log_time(f"Time taken for loading parser: {time.time() - time_start:.2f}s")
        self.interactive = self.base_parser.parse_interactive('')
        self.parsed_lexer_tokens: list = []
        self.prev_lexer_tokens: list[Token] = [] # To enable going back to old state of the parser
        self.cur_pos_to_parser_state: dict[int, Tuple[Any, set, set, Optional[list], list]] = {} # parser_state, cur_ac_terminals, next_ac_terminals, indent_levels (optional), dedent_queue
        self.time_accepts = 0 # Profiling

        self.cur_ac_terminals: set = set()
        self.next_ac_terminals: set = self._accepts(self.interactive)

    def reset(self):
        """
        Resets the parser to the initial state.
        """
        self.cur_pos = 0
        self.lexer_pos = 0
        self.dedent_queue = []
        self.parsed_lexer_tokens = []
        self.prev_lexer_tokens = []
        self.cur_pos_to_parser_state = {}
        self.time_accepts = 0
        self.interactive = self.base_parser.parse_interactive('')
        self.cur_ac_terminals = set()
        self.next_ac_terminals = self._accepts(self.interactive)
    
    def _store_parser_state(self, pos: int, parser_state, accepts: set, indent_levels: Optional[list] = None):  
        time_start = time.time() 
        cur_ac_terminals = self.next_ac_terminals  
        next_ac_terminals = accepts 
        
        # parser_state, cur_ac_terminals, next_ac_terminals, indent_levels, dedent_queue
        self.cur_pos_to_parser_state[pos] = (copy.deepcopy(self.parsed_lexer_tokens), parser_state, cur_ac_terminals, next_ac_terminals, indent_levels, copy.deepcopy(self.dedent_queue))
        
        self.cur_ac_terminals = copy.deepcopy(cur_ac_terminals)
        self.next_ac_terminals = copy.deepcopy(next_ac_terminals)
        self.logger.log_time(f'Time taken for storing parser state:{time.time() - time_start}')

    def _restore_parser_state(self, pos: int):
        time_start = time.time()
        parsed_lexer_tokens, parser_state, cur_ac_terminals, next_ac_terminals, indent_levels, dedent_queue = self.cur_pos_to_parser_state[pos]
        
        self.interactive.parser_state = parser_state.copy()
        self.parsed_lexer_tokens = copy.deepcopy(parsed_lexer_tokens)
        self.dedent_queue = copy.deepcopy(dedent_queue)
        self.cur_ac_terminals = copy.deepcopy(cur_ac_terminals)
        self.next_ac_terminals = copy.deepcopy(next_ac_terminals)

        if indent_levels is not None:
            self.indent_level = copy.deepcopy(indent_levels)

        self.logger.log_time(f'Time taken for restoring parser state:{time.time() - time_start}')

    def _lex_code(self, code) -> Tuple[Iterable[Token], bool]:
        """
        Lexes the given code and returns the list of tokens.
        """
        # Collect Lexer tokens
        lexer_tokens: Iterable[Token] = []
        interactive = self.base_parser.parse_interactive(code)
        lexing_start_time = time.time()
        lexer_state = interactive.lexer_thread.state
        lexing_incomplete = False
        try:
            while lexer_state.line_ctr.char_pos < len(lexer_state.text):
                blexer = interactive.lexer_thread.lexer
                token = blexer.next_token(lexer_state)
                self.lexer_pos = lexer_state.line_ctr.char_pos
                lexer_tokens.append(token)
        except lark.exceptions.UnexpectedCharacters as e:
            lexing_incomplete = True
            # We update the lexer position to the current position since the lexer has stopped at this position
            self.lexer_pos = lexer_state.line_ctr.char_pos
        except EOFError as e:
            pass
    
        self.logger.log_time(f'Time taken for lexing:{time.time() - lexing_start_time}')
        return lexer_tokens, lexing_incomplete
    
    def _restore_recent_parser_state(self, lexer_tokens):
        """
        Restores the parser state to the most recent prefix matching state that was stored. 
        """
        max_matching_index = -1
        for i in range(min(len(self.prev_lexer_tokens), len(lexer_tokens))):
            if self.prev_lexer_tokens[i] != lexer_tokens[i]:
                break
            if i in self.cur_pos_to_parser_state:
                max_matching_index = i

        if max_matching_index != -1:
            self.cur_pos = max_matching_index + 1
            assert (max_matching_index) in self.cur_pos_to_parser_state
            self._restore_parser_state(max_matching_index)
        else:
            self.cur_pos = 0


    def get_acceptable_next_terminals(self, partial_code) -> ParseResult:
        """
        Returns the set of acceptable terminals at the current partial code position.
        """
        # Stores the sequence of tokens that the parser has seen in the order  
        interactive = self.interactive
        lexer_tokens, lexing_incomplete = self._lex_code(partial_code)
        self.next_ac_terminals = self._accepts(interactive)

        # Restore the previous state of the parser
        if len(self.prev_lexer_tokens) > 0:
            self._restore_recent_parser_state(lexer_tokens)

        self.prev_lexer_tokens = lexer_tokens  # Set the previous lexer tokens

        # Parse the tokens
        parsing_start_time = time.time()
        self.time_accepts = 0
        parse_incomplete = False
        
        try:
            while self.cur_pos < len(lexer_tokens):
                token = lexer_tokens[self.cur_pos]
                self.cur_pos += 1
                self.parsed_lexer_tokens.append(token) # parser_token_seq holds all tokens
                interactive.feed_token(token)

                # Store the current state of the parser
                self._store_parser_state(
                    self.cur_pos-1, 
                    interactive.parser_state.copy(), 
                    self._accepts(interactive))

        except lark.exceptions.UnexpectedToken as e:
            parse_incomplete = True
            self._handle_parsing_error(lexer_tokens, token)

        self.logger.log_time(f'Time taken for parsing:{time.time() - parsing_start_time}')
        self.logger.log_time(f'Time taken for computing accepts:{self.time_accepts}')

        # Compute current terminal string
        remainder_state, current_term_str, final_terminal = self._get_remainder(partial_code, lexing_incomplete=lexing_incomplete, parse_incomplete=parse_incomplete)            
        
        return ParseResult.from_accept_terminals(self.cur_ac_terminals, self.next_ac_terminals, current_term_str, remainder_state, final_terminal=final_terminal, ignore_terminals=self.base_parser.lexer_conf.ignore)

    def _get_remainder(self, code, lexing_incomplete=False, parse_incomplete=False):
        final_terminal = None
        if lexing_incomplete: # Lexing is incomplete
            current_term_str = code[self.lexer_pos:]
            current_term_str = current_term_str.lstrip(' ') # Remove space from the beginning
            if current_term_str == '':
                remainder_state = RemainderState.COMPLETE
            else: 
                remainder_state = RemainderState.INCOMPLETE
                self.cur_ac_terminals = self.next_ac_terminals
                self.next_ac_terminals = set()
        elif parse_incomplete: # Parsing is incomplete
            remainder_state = RemainderState.INCOMPLETE
            current_term_str = self.parsed_lexer_tokens[-1].value
            final_terminal = self.parsed_lexer_tokens[-1].type
        elif len(self.parsed_lexer_tokens) > 0:
            if self.lexer_pos < len(code): # In this case the final lexical tokens are ignored by the parser
                remainder_state = RemainderState.COMPLETE
                current_term_str = ''
            else:
                # Although this is a complete terminal, it may happen that this may be just prefix of some other terminal
                # e.g., 'de' may seem like a variable name that is complete, but it may be just a prefix of 'def'
                current_term_str = self.parsed_lexer_tokens[-1].value
                remainder_state = RemainderState.MAYBE_COMPLETE
                final_terminal = self.parsed_lexer_tokens[-1].type
        else:
            # When the code is empty
            remainder_state = RemainderState.COMPLETE
            current_term_str = ''
        return remainder_state, current_term_str, final_terminal
    
    def _accepts(self, interactive_parser: InteractiveParser) -> set:
        start_time = time.time()
        accepts = interactive_parser.accepts()
        self.time_accepts += time.time() - start_time
        return accepts
    
    def _handle_parsing_error(self, lexer_tokens, token):
        """
        Handles the error that occurs when the lexer token is not parsed correctly.
        1. If the final token is not parsed correctly, then it is okay.
        2. If a non-final token is not parsed correctly, then it is an issue. We log the warning in that case. 
        """
        if token != lexer_tokens[-1]:
            self.logger.log_error(f'Error in parsing the token: {token} which is not the last token in the lexer_tokens: {lexer_tokens}')
        else:
            # If it is the final token that gave the error, then it is okay
            self.cur_ac_terminals = self.next_ac_terminals
            self.next_ac_terminals = set()
