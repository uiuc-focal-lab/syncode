import time
import lark
import regex
from lark.indenter import Indenter
from incremental_parser import IncrementalParser
from parse_result import ParseResult, RemainderState


class PythonIndenter(Indenter):
        NL_type = "_NL"
        OPEN_PAREN_types = ["LPAR", "LSQB", "LBRACE"]
        CLOSE_PAREN_types = ["RPAR", "RSQB", "RBRACE"]
        INDENT_type = "_INDENT"
        DEDENT_type = "_DEDENT"
        tab_len = 4


class PythonIncrementalParser(IncrementalParser):
    """
    This class implements an incremental parser for Python code.
    """
    def __init__(self, partial_code=None):
        indenter = PythonIndenter()
        super().__init__("llm_cfg/grammars/python_grammar.lark", indenter=indenter)

        if partial_code is not None: # extract indentation type from partial code
            indenter.tab_len = self._get_indentation(partial_code)  # NOTE: tab_len is useful when \t and spaces are used for indentation in same code 

    def _get_indentation(self, partial_code) -> int:
        m = regex.match(r"(.*?):(.*?)\n(.*?)(?![ \t])", partial_code, flags=regex.DOTALL)
        indent_type = m.group(3)
        tab_len = 4 # Default tab length
        if '\t' not in indent_type: # that means we are using spaces for indentation
            tab_len = indent_type.count(' ')
        return tab_len

    def get_acceptable_next_terminals(self, code) -> ParseResult:
        # Stores the sequence of tokens that the parser has seen in the order  
        interactive = self.interactive
        lexer_tokens = self._lex_code(code)

        # Restore the previous state of the parser
        if self.prev_lexer_tokens is not None:
            # Find the maximum index such that the tokens are same and the parser state is stored
            max_matching_index = -1
            for i in range(min(len(self.prev_lexer_tokens), len(lexer_tokens))):
                if self.prev_lexer_tokens[i] != lexer_tokens[i]:
                    break
                if i in self.cur_pos_to_interactive:
                    max_matching_index = i

            if max_matching_index != -1:
                self.cur_pos = max_matching_index + 1
                # print('********Restoring parser state 1!', max_matching_index )
                # print(self.prev_lexer_tokens[self.cur_pos-1], lexer_tokens[self.cur_pos-1])
                assert (max_matching_index) in self.cur_pos_to_interactive
                self._restore_parser_state(max_matching_index)

        # Set the previous lexer tokens
        self.prev_lexer_tokens = lexer_tokens

        # Parse the tokens
        parsing_start_time = time.time()
        try:
            while self.cur_pos < len(lexer_tokens):
                token = lexer_tokens[self.cur_pos]
                # print(self.cur_pos, repr(token), repr(lexer_tokens[self.cur_pos]))
                self.cur_pos += 1
                # print(self.cur_pos, repr(token), interactive.parser_state.state_stack, len(interactive.parser_state.state_stack), len(self.dedent_queue))
                if token.type == '_INDENT':
                    self.cur_indentation_level += 1
                elif token.type == '_DEDENT':
                    # Do not shoot dedent tokens unless there is some code on the next line
                    self.dedent_queue.append(token)
                    continue
                else:
                    self.parser_token_seq.append(token) # parser_token_seq holds all tokens except _INDENT and _DEDENT

                    while not len(self.dedent_queue)==0: # Shoot all the dedent tokens that are in the queue
                        dedent_token = self.dedent_queue.pop()
                        self.cur_indentation_level -= 1
                        interactive.feed_token(dedent_token)
                # TODO: Check if there is an overhead of computing accept tokens
                interactive.feed_token(token)

                # Store the current state of the parser
                self._store_parser_state(self.cur_pos-1, interactive.parser_state.copy(), self.cur_indentation_level, interactive.accepts())

        except lark.exceptions.UnexpectedToken as e:
            # print(e)
            pass

        if self.log_time:
            print('Time taken for parsing:', (time.time() - parsing_start_time))

        reminder_state = None
        # Compute current terminal string
        if self.lexer_pos < len(code):
            reminder_state = RemainderState.INCOMPLETE
            current_term_str = code[self.lexer_pos:]
            # print('current_term_str 1:', repr(current_term_str))

            current_term_str = current_term_str.lstrip(' ') # Remove space from the beginning
            if current_term_str == '':
                reminder_state = RemainderState.COMPLETE
        else:
            # Although this is a complete terminal, it may happen that this may be just prefix of some other terminal
            # e.g., 'de' may seem like a variable name that is complete, but it may be just a prefix of 'def'
            current_term_str = self.parser_token_seq[-1].value
            reminder_state = RemainderState.MAYBE_COMPLETE
            # print('current_term_str 2:', current_term_str, self.parser_token_seq)

        if reminder_state == RemainderState.MAYBE_COMPLETE or reminder_state == RemainderState.COMPLETE:
            if self.parser_token_seq[-1].type == '_NL':
                # Compute next line accepted indentation levels
                max_next_indentation_level = 0
                # print('next_ac_terminals:', next_ac_terminals)

                if '_INDENT' in self.next_ac_terminals:
                    max_next_indentation_level = self.cur_indentation_level + 1
                elif '_DEDENT' in self.next_ac_terminals and len(self.next_ac_terminals)==1:
                    max_next_indentation_level = self.cur_indentation_level - 1
                elif '_DEDENT' in self.next_ac_terminals and len(self.next_ac_terminals)>1:
                    max_next_indentation_level = self.cur_indentation_level

                cur_tabs = self.parser_token_seq[-1].value.split('\n')[-1].count('\t')

                # Remove the _INDENT and _DEDENT tokens from the acceptable tokens
                # since we inform the indentation level through the _TAB token
                if '_INDENT' in self.next_ac_terminals:
                    self.next_ac_terminals.remove('_INDENT')
                if '_DEDENT' in self.next_ac_terminals:
                    self.next_ac_terminals.remove('_DEDENT')

                # '_NL' is always accepted in this case
                self.next_ac_terminals.add('_NL')

                if cur_tabs < max_next_indentation_level:
                    # print('Expect a tab!')
                    self.next_ac_terminals.add('_TAB')
                # elif cur_tabs > max_next_indentation_level:
                #     raise Exception('Invalid indentation level! max_next_indentation_level: {}, cur_tabs: {}'.format(max_next_indentation_level, cur_tabs))

        else: # Since current terminal is incomplete, next token should add to current terminal
            self.next_ac_terminals = None

        if self.next_ac_terminals is not None and '_NL' in self.next_ac_terminals:
            self.next_ac_terminals.add('COMMENT')

        return ParseResult(self.cur_ac_terminals, self.next_ac_terminals, current_term_str, reminder_state)

    def _lex_code(self, code: str) -> list:
        # Collect Lexer tokens
        lexer_tokens = []
        interactive = self.parser.parse_interactive(code)
        lexing_start_time = time.time()
        lexer_state = interactive.lexer_thread.state
        indenter: Indenter = self.parser.lexer_conf.postlex

        # Reset the indentation level
        indenter.indent_level, indenter.paren_level = [0], 0
        # print('Starting indent level:', indenter.indent_level)

        try:
            while lexer_state.line_ctr.char_pos < len(lexer_state.text):
                blexer = interactive.lexer_thread.lexer.lexer
                token = blexer.next_token(lexer_state)
                self.lexer_pos = lexer_state.line_ctr.char_pos
                # Perform postlexing indentation
                if token.type == indenter.NL_type:
                    # print('NL token:', indenter.indent_level)
                    lexer_tokens += indenter.handle_NL(token)
                else:
                    lexer_tokens.append(token)

                if token.type in indenter.OPEN_PAREN_types:
                        indenter.paren_level += 1
                elif token.type in indenter.CLOSE_PAREN_types:
                        indenter.paren_level -= 1
                        assert indenter.paren_level >= 0
        except lark.exceptions.UnexpectedCharacters as e:
            pass
        except EOFError as e:
            # print('EOF Error!')
            # print(code)
            # print(lexer_state.line_ctr.char_pos, len(lexer_state.text))
            pass
            # raise e

        if self.log_time:
            print('Time taken for lexing:', time.time() - lexing_start_time)
        # print(lexer_tokens)
        return lexer_tokens
    