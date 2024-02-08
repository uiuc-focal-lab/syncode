import time
import larkm as lark
from parsers.incremental_parser import IncrementalParser
from parse_result import ParseResult, RemainderState


class GoIncrementalParser(IncrementalParser):
    """
    This class implements an incremental parser for Go code.
    """

    def __init__(self, base_parser, **kwargs):
        super().__init__(base_parser, **kwargs)


    def get_acceptable_next_terminals(self, partial_code) -> ParseResult:
        """
        Returns the set of acceptable terminals at the current partial code position.
        """
        # Stores the sequence of tokens that the parser has seen in the order  
        interactive = self.interactive
        lexer_tokens: list[lark.Token] = self._lex_code(partial_code)

        # Restore the previous state of the parser
        self._restore_recent_parser_state(lexer_tokens)
        
        self.prev_lexer_tokens = lexer_tokens  # Set the previous lexer tokens

        # Parse the tokens
        parsing_start_time = time.time()
        self.time_accepts = 0

        try:
            while self.cur_pos < len(lexer_tokens):
                token = lexer_tokens[self.cur_pos]
                self.cur_pos += 1

                if token.type == 'EOS' and self.next_ac_terminals is not None:
                    if 'EOS' not in self.next_ac_terminals:
                        continue

                self.parser_token_seq.append(token) # parser_token_seq holds all tokens
                interactive.feed_token(token)
                
                # Store the current state of the parser
                self._store_parser_state(
                    self.cur_pos-1, 
                    interactive.parser_state.copy(), 
                    self._accepts(interactive)
                    )
        except lark.exceptions.UnexpectedToken as e:
            self._handle_parsing_error(lexer_tokens, token)
        
        self.logger.log_time(f'Time taken for parsing:{time.time() - parsing_start_time}')
        self.logger.log_time(f'Time taken for computing accepts:{self.time_accepts}')
        self.next_ac_terminals.add('EOS')
        
        # Compute current terminal string
        remainder_state, current_term_str, final_terminal = self._get_remainder(partial_code)

        if remainder_state == RemainderState.INCOMPLETE:
            self.cur_ac_terminals = self.next_ac_terminals
            self.next_ac_terminals = set()
            
        return ParseResult.from_accept_terminals(self.cur_ac_terminals, self.next_ac_terminals, current_term_str, remainder_state, final_terminal=final_terminal, ignore_terminals=self.base_parser.ignore_tokens)
    