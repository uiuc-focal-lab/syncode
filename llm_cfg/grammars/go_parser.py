import time
import lark
from incremental_parser import IncrementalParser
from parse_result import ParseResult


class GoIncrementalParser(IncrementalParser):
    """
    This class implements an incremental parser for Python code.
    """

    def __init__(self):
        super().__init__("llm_cfg/grammars/go_grammar.lark")


    def get_acceptable_next_terminals(self, partial_code) -> ParseResult:
        """
        Returns the set of acceptable terminals at the current partial code position.
        """
        # Stores the sequence of tokens that the parser has seen in the order  
        interactive = self.interactive
        lexer_tokens: list[lark.Token] = self._lex_code(partial_code)

        # Restore the previous state of the parser
        self._restore_recent_parser_state(lexer_tokens)
        
        self.prev_lexer_tokens, next_ac_tokens = lexer_tokens, None  # Set the previous lexer tokens

        # Parse the tokens
        parsing_start_time = time.time()
        try:
            while self.cur_pos < len(lexer_tokens):
                token = lexer_tokens[self.cur_pos]
                # print(self.cur_pos, repr(token))
                self.cur_pos += 1

                if token.type == 'EOS' and next_ac_tokens is not None:
                    if 'EOS' not in next_ac_tokens:
                        continue

                self.parser_token_seq.append(token) # parser_token_seq holds all tokens
                interactive.feed_token(token)

                # Store the current state of the parser
                next_ac_tokens = interactive.accepts()
                self._store_parser_state(self.cur_pos-1, interactive.parser_state.copy(), next_ac_tokens)

        except lark.exceptions.UnexpectedToken as e:
            pass

        if self.log_time:
            print('Time taken for parsing:', (time.time() - parsing_start_time))

        # Compute current terminal string
        remainder_state, current_term_str = self._get_remainder(partial_code)
        
        return ParseResult(self.cur_ac_terminals, self.next_ac_terminals, current_term_str, remainder_state)