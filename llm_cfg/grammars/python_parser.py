import time
from typing import Iterator
import lark
import regex
from lark import Token
from lark.indenter import Indenter
from incremental_parser import IncrementalParser
from parse_result import IndentationConstraint, ParseResult, RemainderState


class PythonIndenter(Indenter):
        NL_type = "_NL"
        OPEN_PAREN_types = ["LPAR", "LSQB", "LBRACE"]
        CLOSE_PAREN_types = ["RPAR", "RSQB", "RBRACE"]
        INDENT_type = "_INDENT"
        DEDENT_type = "_DEDENT"
        tab_len = 4

        def _handle_NL(self, token: Token) -> Iterator[Token]:
            '''
            This is taken from Lark library and modified to handle the case when there is a LONG_STRING comment in the _NL token.
            '''
            if self.paren_level > 0:
                return

            m = regex.match(r'(.*)(\'\'\'.*?\'\'\'|""".*?""")(.*)', token.value, flags=regex.DOTALL)
            if m is not None: # There is a LONG_STRING comment in the _NL token
                indent_str = m.group(1).rsplit('\n', 1)[1] # Tabs and spaces
                indent = indent_str.count(' ') + indent_str.count('\t') * self.tab_len
                self.indent_level.append(indent)
                yield Token.new_borrow_pos(self.NL_type, m.group(0), token)
                yield Token.new_borrow_pos(self.INDENT_type, indent_str, token) 
                yield Token.new_borrow_pos('LONG_STRING', m.group(1), token)

            yield token

            indent_str = token.rsplit('\n', 1)[1] # Tabs and spaces
            indent = indent_str.count(' ') + indent_str.count('\t') * self.tab_len

            if indent > self.indent_level[-1]:
                self.indent_level.append(indent)
                yield Token.new_borrow_pos(self.INDENT_type, indent_str, token)
            else:
                while indent < self.indent_level[-1]:
                    self.indent_level.pop()
                    yield Token.new_borrow_pos(self.DEDENT_type, indent_str, token)


class PythonIncrementalParser(IncrementalParser):
    """
    This class implements an incremental parser for Python code.
    """
    def __init__(self, partial_code=None):
        indenter = PythonIndenter()
        super().__init__("llm_cfg/grammars/python_grammar.lark", indenter=indenter)

        if partial_code is not None: # extract indentation type from partial code
            indenter.tab_len = self._get_indentation(partial_code)  # NOTE: tab_len is useful when \t and spaces are used for indentation in same code
        self.tab_len = indenter.tab_len
        self.indent_level = [0] # Current indentation level

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

        
        self.prev_lexer_tokens = lexer_tokens  # Set the previous lexer tokens
        next_ac_indents = None

        # Parse the tokens
        parsing_start_time = time.time()
        try:
            while self.cur_pos < len(lexer_tokens):
                token = lexer_tokens[self.cur_pos]
                # print(self.cur_pos, repr(token), self.indent_level)
                self.cur_pos += 1

                if token.type == '_INDENT':
                    indent = token.count(' ') + token.count('\t') * self.tab_len
                    self._update_indent_levels(self.indent_level, indent)            
                elif token.type == '_DEDENT': # Do not shoot dedent tokens unless there is some code on the next line
                    self.dedent_queue.append(token)
                    continue
                else:
                    self.parser_token_seq.append(token) # parser_token_seq holds all tokens except _INDENT and _DEDENT

                    while not len(self.dedent_queue)==0: # Shoot all the dedent tokens that are in the queue
                        self.indent_level.pop()
                        dedent_token = self.dedent_queue.pop()
                        interactive.feed_token(dedent_token)
                
                interactive.feed_token(token)

                # Store the current state of the parser
                self._store_parser_state(self.cur_pos-1, interactive.parser_state.copy(), interactive.accepts())

        except lark.exceptions.UnexpectedToken as e:
            pass

        if self.log_time:
            print('Time taken for parsing:', (time.time() - parsing_start_time))

        remainder_state = None
        # Compute current terminal string
        if self.lexer_pos < len(code):
            remainder_state = RemainderState.INCOMPLETE
            current_term_str = code[self.lexer_pos:]
            # print('current_term_str 1:', repr(current_term_str))

            current_term_str = current_term_str.lstrip(' ') # Remove space from the beginning
            if current_term_str == '':
                remainder_state = RemainderState.COMPLETE
        else:
            # Although this is a complete terminal, it may happen that this may be just prefix of some other terminal
            # e.g., 'de' may seem like a variable name that is complete, but it may be just a prefix of 'def'
            current_term_str = self.parser_token_seq[-1].value
            remainder_state = RemainderState.MAYBE_COMPLETE
            # print('current_term_str 2:', current_term_str, self.parser_token_seq)

        next_ac_indents = None
        if remainder_state == RemainderState.MAYBE_COMPLETE or remainder_state == RemainderState.COMPLETE:
            if self.parser_token_seq[-1].type == '_NL':
                last_indent_str = self.parser_token_seq[-1].value.split('\n')[-1]
                last_indent = last_indent_str.count(' ') + last_indent_str.count('\t') * self.tab_len
                next_ac_indents = [indent-last_indent for indent in self.indent_level if indent >= last_indent]

                if '_INDENT' in self.next_ac_terminals:
                    next_ac_indents = IndentationConstraint(greater_than_indent_val=next_ac_indents[-1]) # next indentation level in this case
                elif '_INDENT' in self.cur_ac_terminals:
                    next_ac_indents = IndentationConstraint(greater_than_indent_val=next_ac_indents[-1]-1)
                else:  
                    next_ac_indents = IndentationConstraint(accept_indents=next_ac_indents)  

                self.next_ac_terminals.add('_NL') # '_NL' is always accepted in this case

        else: # Since current terminal is incomplete, next token should add to current terminal
            self.next_ac_terminals = None

        if self.next_ac_terminals is not None and '_NL' in self.next_ac_terminals:
            self.next_ac_terminals.add('COMMENT')

        return ParseResult(self.cur_ac_terminals, self.next_ac_terminals, current_term_str, remainder_state, next_ac_indents=next_ac_indents)

    def _update_indent_levels(self, indent_level, indent):
        # if self.cur_pos != len(lexer_tokens): # Store previous indentation levels except the last one
        if indent > indent_level[-1]:
            indent_level.append(indent)
        else:
            while indent < indent_level[-1]:
                indent_level.pop()

    def _lex_code(self, code: str) -> list[Token]:
        # Collect Lexer tokens
        lexer_tokens: list[Token] = []
        interactive = self.parser.parse_interactive(code)
        lexing_start_time = time.time()
        lexer_state = interactive.lexer_thread.state
        indenter: PythonIndenter = self.parser.lexer_conf.postlex

        # Reset the indentation level
        indenter.indent_level, indenter.paren_level = [0], 0

        try:
            while lexer_state.line_ctr.char_pos < len(lexer_state.text):
                blexer = interactive.lexer_thread.lexer.lexer
                token = blexer.next_token(lexer_state)
                self.lexer_pos = lexer_state.line_ctr.char_pos
                
                # Perform postlexing indentation
                if token.type == indenter.NL_type:
                    lexer_tokens += indenter._handle_NL(token)
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
            pass

        if self.log_time:
            print('Time taken for lexing:', time.time() - lexing_start_time)
        return lexer_tokens
    