import copy
from syncode.larkm.tree import Tree
from syncode.larkm.parsers.lalr_analysis import Reduce
from syncode.larkm.parsers.lalr_parser_state import ParserState
import syncode.common as common
import syncode.larkm as lark
from syncode.larkm.parsers.lalr_interactive_parser import InteractiveParser
from syncode.parse_result import ParseResult, RemainderState
from syncode.larkm.lexer import Token
from typing import Optional, Any, Tuple, Iterable
from collections import defaultdict

class SymbolPosMap:
    """
    This class stores the mapping of the symbols to their positions in the code as a map of symbol to list of positions. The list of positions is sorted in increasing order. 
    A position is a tuple of start and end position of the symbol in the code.

    Example:
    symbol_pos_map = {
        'NUMBER': [(0, 2), (4, 6), (8, 10)],
        'OPERATOR': [(3, 3), (7, 7)]
    }
    """
    def __init__(self):
        self._pos_map = defaultdict(list)
    
    def add_symbol_pos(self, symbol:str, pos:Tuple[int, int]):
        """
        Adds the position of the symbol in the code.
        """
        start_pos, _ = pos

        if len(self._pos_map[symbol]) == 0 or self._pos_map[symbol][-1][0] != start_pos:
            self._pos_map[symbol].append(pos)
        elif self._pos_map[symbol][-1][0] == start_pos:
            self._pos_map[symbol][-1] = pos

    def get_symbol_pos_start(self, symbol:str, idx:int) -> int:
        """
        Returns the k-th position of the symbol in the code.
        """
        return self._pos_map[symbol][idx][0]
    
    def get_symbol_pos_end(self, symbol:str, idx:int) -> int:
        """
        Returns the k-th position of the symbol in the code.
        """
        return self._pos_map[symbol][idx][1]

    def get_symbol_pos_all(self, symbol:str) -> list:
        """
        Returns all the positions of the symbol in the code.
        """
        return self._pos_map[symbol]

    def get_symbol_count(self, symbol: str, after: int=0) -> int:
        """
        Returns the number of times the symbol is present in the code after the given position.
        """
        return len([pos for pos in self._pos_map[symbol] if pos[1] > after])
    
    def crop(self, target_char_pos:int):
        """
        Updates the symbol pos map and removes the positions that are greater than the target_char_pos.
        """
        for symbol, pos_list in self._pos_map.items():
            self._pos_map[symbol] = [pos for pos in pos_list if pos[1] <= target_char_pos]
    
    def is_present(self, symbol:str) -> bool:
        """
        Returns True if the symbol is present in the symbol pos map.
        """
        return symbol in self._pos_map
                

class IncrementalParser:    
    """
    This is the base class for all incremental parsers.
    """
    def __init__(self, base_parser, logger: Optional[common.Logger]=None, ignore_whitespace=False) -> None:
        self.cur_pos = 0 # Current cursor position in the lexer tokens list
        self.lexer_pos = 0 # Current lexer position in the code
        self.dedent_queue: list = []
        self._ignore_whitespace = ignore_whitespace

        # Initialize the parser
        self.base_parser = base_parser

        self.logger = logger if logger is not None else common.EmptyLogger()
        self.interactive = self.base_parser.parse_interactive('')
        self.parsed_lexer_tokens: list = []
        self.cur_pos_to_parser_state: dict[int, Tuple[Any, set, set, Optional[list], list]] = {} # parser_state, cur_ac_terminals, next_ac_terminals, indent_levels (optional), dedent_queue

        self.cur_ac_terminals: set = set()
        self.next_ac_terminals: set = self._accepts(self.interactive)
        self.symbol_pos_map: SymbolPosMap = SymbolPosMap()

    def reset(self):
        """
        Resets the parser to the initial state.
        """
        self.cur_pos_to_parser_state = {}
        self.lexer_pos = 0

        # Reset maps used to mark units 
        self.symbol_pos_map = SymbolPosMap()

        # Reset the parser state
        self._set_initial_parser_state()
        

    def _set_initial_parser_state(self):
        self.cur_pos = 0
        self.dedent_queue = []
        self.parsed_lexer_tokens = []
        self.interactive = self.base_parser.parse_interactive('')
        self.cur_ac_terminals = set()
        self.next_ac_terminals = self._accepts(self.interactive)
    

    def _store_parser_state(self, pos: int, lexer_tokens: Iterable[Token], parser_state, accepts: set, indent_levels: Optional[list] = None):
        """
        Make immutable copies of the parser state and restore the parser state to the given position.
        """  
        cur_ac_terminals = self.next_ac_terminals  
        next_ac_terminals = accepts 

        # Create a hash of lexer tokens till position pos
        key = self._get_hash(lexer_tokens[:pos+1])
        
        # parser_state, cur_ac_terminals, next_ac_terminals, indent_levels, dedent_queue
        self.cur_pos_to_parser_state[key] = (copy.deepcopy(self.parsed_lexer_tokens), parser_state, cur_ac_terminals, next_ac_terminals, indent_levels, copy.deepcopy(self.dedent_queue), copy.deepcopy(self.symbol_pos_map))
        # self.cur_pos_to_parser_state[pos] = (copy.deepcopy(self.parsed_lexer_tokens), parser_state, cur_ac_terminals, next_ac_terminals, indent_levels, copy.deepcopy(self.dedent_queue))
        
        self.cur_ac_terminals = copy.deepcopy(cur_ac_terminals)
        self.next_ac_terminals = copy.deepcopy(next_ac_terminals)

    def _restore_parser_state(self, key: int):
        """
        Restore immutable copies of the parser state and restore the parser state to the given position.
        """
        parsed_lexer_tokens, parser_state, cur_ac_terminals, next_ac_terminals, indent_levels, dedent_queue, symbol_pos_map = self.cur_pos_to_parser_state[key]
        # parsed_lexer_tokens, parser_state, cur_ac_terminals, next_ac_terminals, indent_levels, dedent_queue = self.cur_pos_to_parser_state[pos]
        
        self.interactive.parser_state = parser_state.copy()
        self.parsed_lexer_tokens = copy.deepcopy(parsed_lexer_tokens)
        self.dedent_queue = copy.deepcopy(dedent_queue)
        self.cur_ac_terminals = copy.deepcopy(cur_ac_terminals)
        self.next_ac_terminals = copy.deepcopy(next_ac_terminals)
        self.symbol_pos_map = copy.deepcopy(symbol_pos_map)

        if indent_levels is not None:
            self.indent_level = copy.deepcopy(indent_levels)


    def _lex_code(self, code) -> Tuple[Iterable[Token], bool]:
        """
        Lexes the given code and returns the list of tokens.
        """
        # Collect Lexer tokens
        lexer_tokens: Iterable[Token] = []
        interactive = self.base_parser.parse_interactive(code)
        lexer_state = interactive.lexer_thread.state
        lexing_incomplete = False
        try:
            while lexer_state.line_ctr.char_pos < len(lexer_state.text):
                blexer = interactive.lexer_thread.lexer
                token = blexer.next_token(lexer_state)
                self.lexer_pos = lexer_state.line_ctr.char_pos

                if len(lexer_tokens)>0 and token.start_pos > lexer_tokens[-1].end_pos:
                    # We have a gap in the tokens. This can happen if we had ignored tokens in the middle
                    lexer_tokens.append(Token('IGNORED', None, start_pos=lexer_tokens[-1].end_pos))
                lexer_tokens.append(token)

        except lark.exceptions.UnexpectedCharacters as e:
            lexing_incomplete = True
            # We update the lexer position to the current position since the lexer has stopped at this position
            self.lexer_pos = lexer_state.line_ctr.char_pos
        except EOFError as e:
            pass
        
        if len(lexer_tokens)>0 and lexer_tokens[-1].end_pos < len(code):
            # We have a gap in the tokens. This can happen if we had ignored token at the end
            lexer_tokens.append(Token('IGNORED', None, start_pos=lexer_tokens[-1].end_pos))

        return lexer_tokens, lexing_incomplete
    

    def _restore_recent_parser_state(self, lexer_tokens):
        """
        Restores the parser state to the most recent prefix matching state that was stored. 
        """
        max_stored_index = -1
        idx = len(lexer_tokens)-1
        
        while idx >= 0:
            # TODO: This is not the best way to hash the lexer tokens. We should use a better hashing mechanism with some sliding window. 
            key = self._get_hash(lexer_tokens[:idx+1])
            if key in self.cur_pos_to_parser_state:
                max_stored_index = idx
                break
            idx -= 1

        if max_stored_index != -1:
            self.cur_pos = max_stored_index + 1
            key = self._get_hash(lexer_tokens[:max_stored_index+1])
            self._restore_parser_state(key)
        else:
            self._set_initial_parser_state()

    def _get_hash(self, lexer_tokens: Iterable[Token]) -> int:
        return hash(tuple(lexer_tokens))
    

    def get_acceptable_next_terminals(self, partial_code) -> ParseResult:
        """
        Returns the set of acceptable terminals at the current partial code position.
        """
        # Stores the sequence of tokens that the parser has seen in the order  
        interactive = self.interactive
        lexer_tokens, lexing_incomplete = self._lex_code(partial_code)
        self.next_ac_terminals = self._accepts(interactive)

        # Restore the previous state of the parser
        self._restore_recent_parser_state(lexer_tokens)

        self._update_symbol_pos_map_terminals(lexer_tokens)

        # Parse the tokens
        self.time_accepts = 0
        parse_incomplete = False
        
        try:
            while self.cur_pos < len(lexer_tokens):
                token = lexer_tokens[self.cur_pos]
                self.cur_pos += 1
                
                # Update the symbol position map. This should be called before updating the parser state
                self._update_symbol_pos_map_nonterminals(interactive.parser_state, token)

                # Compute the number of characters in the input before the token
                if token.type != 'IGNORED':
                    self.parsed_lexer_tokens.append(token) # parser_token_seq holds all tokens
                    interactive.feed_token(token)
                else:
                    continue

                # Store the current state of the parser
                self._store_parser_state(
                    self.cur_pos-1, 
                    lexer_tokens,
                    interactive.parser_state.copy(), 
                    self._accepts(interactive))

        except lark.exceptions.UnexpectedToken as e:
            parse_incomplete = True
            self._handle_parsing_error(lexer_tokens, token)

        # Compute current terminal string
        remainder_state, current_term_str, final_terminal = self._get_remainder(partial_code, lexing_incomplete=lexing_incomplete, parse_incomplete=parse_incomplete)            
        
        return ParseResult.from_accept_terminals(self.cur_ac_terminals, self.next_ac_terminals, current_term_str, remainder_state, final_terminal=final_terminal, ignore_terminals=self.base_parser.lexer_conf.ignore)


    def _get_remainder(self, code, lexing_incomplete=False, parse_incomplete=False):
        final_terminal = None
        if lexing_incomplete: # Lexing is incomplete
            current_term_str = code[self.lexer_pos:]
            
            if self._ignore_whitespace:
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
        accepts = interactive_parser.accepts()
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

    def _update_symbol_pos_map_terminals(self, lexer_tokens):
        """
        Updates the uc_map with the current token for terminals.
        """
        if len(lexer_tokens) > len(self.parsed_lexer_tokens):
            len_parsed = len(self.parsed_lexer_tokens)

            # self.parsed_lexer_tokens does not contain the IGNORED tokens. So, we need to count the number of IGNORED tokens in the parsed_lexer_tokens
            start_idx = 0
            cnt_non_ignore = 0  # Just temporary index to iterate over lexer_tokens

            # This loop should terminate since there are more non-IGNORED tokens in lexer_tokens than in all tokens in self.parsed_lexer_tokens
            while cnt_non_ignore < len_parsed: # skip first len_parsed non IGNORED tokens
                if lexer_tokens[start_idx].type != 'IGNORED': 
                    cnt_non_ignore += 1
                start_idx += 1
            # all new terminals that are unparsed start from start_idx

            # We don't add the last lexer token as it may change in the future
            # Essntially, we don't want IterGen to stop immediatelly after generating terminal which may extend in the future
            start_idx -= 1
            end_idx = len(lexer_tokens)-1

            for idx in range(start_idx, end_idx):
                if lexer_tokens[idx].type != 'IGNORED':
                    self.symbol_pos_map.add_symbol_pos(
                        lexer_tokens[idx].type, 
                        pos=(lexer_tokens[idx].start_pos, lexer_tokens[idx].end_pos)
                        )

    def _update_symbol_pos_map_nonterminals(self, parser_state: ParserState, token: Token):
        """
        Updates the uc_map with the current token for non-terminals. 

        end_pos: The position of the end of reduced non-terminal
        """ 
        end_pos = token.start_pos

        # Copy the parser state
        state_stack = copy.deepcopy(parser_state.state_stack)
        value_stack = copy.deepcopy(parser_state.value_stack)

        states = parser_state.parse_conf.states
        callbacks = parser_state.parse_conf.callbacks

        while True:
            state = state_stack[-1]
            
            if token.type in states[state]:
                action, arg = states[state][token.type]
            elif token.type == 'IGNORED':
                possible_rules = set()
                for term, (action, rule) in states[state].items():
                    if action != Reduce:
                        break
                    possible_rules.add(rule)
                
                if len(possible_rules) == 1:
                    rule = list(possible_rules)[0]
                    action = Reduce
                    arg = rule
                else:
                    break
            else:
                break

            if action is Reduce:
                # reduce+shift as many times as necessary
                rule = arg
                size = len(rule.expansion)
                if size:
                    s = value_stack[-size:]
                    del state_stack[-size:]
                    del value_stack[-size:]
                else:
                    s = []

                assert end_pos is not None
                if type(rule.origin.name) == Token:
                    start_pos = self._get_nonterminal_start_pos(s)
                    # end_pos = self._get_nonterminal_end_pos(s) # Not using now since we are getting the end_pos from the lexer token
                    self.symbol_pos_map.add_symbol_pos(
                            rule.origin.name.value, 
                            pos=(start_pos, end_pos)
                            )

                value = callbacks[rule](s) if callbacks else s

                _, new_state = states[state_stack[-1]][rule.origin.name]
                state_stack.append(new_state)
                value_stack.append(value)
            else:
                break
        
    def _get_nonterminal_start_pos(self, s:Iterable[Tree]) -> int:
        for item in s:
            if type(item) == Token:
                return item.start_pos
            elif item != None:
                # If the item is not None, then it is a tree
                return item.meta.start_pos
        
        # This should not happen
        return -1

    def _get_nonterminal_end_pos(self, s:Iterable[Tree]) -> int:
        for item in reversed(s):
            if type(item) == Token:
                return item.end_pos
            elif item != None:
                # If the item is not None, then it is a tree
                return item.meta.end_pos
        
        return -1
    