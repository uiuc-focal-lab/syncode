import copy
import re
import time
import lark
from parse_result import ParseResult, RemainderState
from lark.lexer import Token
from lark import Lark

class IncrementalParser:    
    """
    This is the base class for all incremental parsers.
    """
    def __init__(self, grammar_file, indenter=None) -> None:
        self.cur_ac_terminals = None
        self.next_ac_terminals = None
        self.cur_pos = 0 # Current cursor position in the lexer tokens list
        self.lexer_pos = 0 # Current lexer position in the code
        self.dedent_queue: list = []

        self.parser = Lark.open( # This is the standard Lark parser
            grammar_file,
            parser="lalr",
            lexer="basic",
            start="file_input",
            postlex=indenter,
            propagate_positions=True,
        )
        self.interactive = self.parser.parse_interactive('')
        self.parser_token_seq: list = []
        self.log_time = False

        # To enable going back to old state of the parser
        self.prev_lexer_tokens: list[Token] = []
        self.cur_pos_to_interactive: dict = {}
    
    def _store_parser_state(self, pos, parser_state, accepts):      
        self.cur_pos_to_interactive[pos] = (parser_state, accepts, copy.deepcopy(self.dedent_queue))
        self.cur_ac_terminals = copy.deepcopy(self.next_ac_terminals)
        self.next_ac_terminals = copy.deepcopy(accepts)

    def _restore_parser_state(self, pos):
        parser_state, self.cur_ac_terminals, dedent_queue = self.cur_pos_to_interactive[pos]
        self.interactive.parser_state = parser_state.copy()
        self.dedent_queue = copy.deepcopy(dedent_queue)

    def _lex_code(self, code) -> list[Token]:
        """
        Lexes the given code and returns the list of tokens.
        """
        # Collect Lexer tokens
        lexer_tokens: list[Token] = []
        interactive = self.parser.parse_interactive(code)
        lexing_start_time = time.time()
        lexer_state = interactive.lexer_thread.state

        try:
            while lexer_state.line_ctr.char_pos < len(lexer_state.text):
                blexer = interactive.lexer_thread.lexer
                token = blexer.next_token(lexer_state)
                self.lexer_pos = lexer_state.line_ctr.char_pos
                lexer_tokens.append(token)
        except lark.exceptions.UnexpectedCharacters as e:
            pass
        except EOFError as e:
            pass
        self.lexer_pos = lexer_state.line_ctr.char_pos
        if self.log_time:
            print('Time taken for lexing:', time.time() - lexing_start_time)
        return lexer_tokens
    
    def _restore_recent_parser_state(self, lexer_tokens):
        """
        Restores the parser state to the most recent prefix matching state that was stored. 
        """
        # Find the maximum index such that the tokens are same and the parser state is stored
        max_matching_index = -1
        for i in range(min(len(self.prev_lexer_tokens), len(lexer_tokens))):
            if self.prev_lexer_tokens[i] != lexer_tokens[i]:
                break
            if i in self.cur_pos_to_interactive:
                max_matching_index = i

        if max_matching_index != -1:
            self.cur_pos = max_matching_index + 1
            assert (max_matching_index) in self.cur_pos_to_interactive
            self._restore_parser_state(max_matching_index)


    def get_acceptable_next_terminals(self, partial_code) -> ParseResult:
        """
        Returns the set of acceptable terminals at the current partial code position.
        """
        # Stores the sequence of tokens that the parser has seen in the order  
        interactive = self.interactive
        lexer_tokens: list[Token] = self._lex_code(partial_code)

        # Restore the previous state of the parser
        if self.prev_lexer_tokens is not None:
            self._restore_recent_parser_state(lexer_tokens)
        
        self.prev_lexer_tokens, next_ac_indents = lexer_tokens, None  # Set the previous lexer tokens

        # Parse the tokens
        parsing_start_time = time.time()
        try:
            while self.cur_pos < len(lexer_tokens):
                token = lexer_tokens[self.cur_pos]
                self.cur_pos += 1
                self.parser_token_seq.append(token) # parser_token_seq holds all tokens
                interactive.feed_token(token)

                # Store the current state of the parser
                self._store_parser_state(self.cur_pos-1, interactive.parser_state.copy(), interactive.accepts())

        except lark.exceptions.UnexpectedToken as e:
            pass

        if self.log_time:
            print('Time taken for parsing:', (time.time() - parsing_start_time))

        # Compute current terminal string
        remainder_state, current_term_str = self._get_remainder(partial_code)
        
        return ParseResult(self.cur_ac_terminals, self.next_ac_terminals, current_term_str, remainder_state, next_ac_indents=next_ac_indents)

    def _get_remainder(self, code):
        if self.lexer_pos < len(code):
            remainder_state = RemainderState.INCOMPLETE
            current_term_str = code[self.lexer_pos:]
            current_term_str = current_term_str.lstrip(' ') # Remove space from the beginning
            if current_term_str == '':
                remainder_state = RemainderState.COMPLETE
        else:
            # Although this is a complete terminal, it may happen that this may be just prefix of some other terminal
            # e.g., 'de' may seem like a variable name that is complete, but it may be just a prefix of 'def'
            current_term_str = self.parser_token_seq[-1].value
            remainder_state = RemainderState.MAYBE_COMPLETE
        return remainder_state,current_term_str
    