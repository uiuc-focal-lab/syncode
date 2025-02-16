"""
Symbol Position Map is used in IterGen to store the mapping of the symbols to their positions in the code as a map of symbol to list of positions.
"""
from collections import defaultdict
import copy
from typing import Iterable, Tuple
from syncode.larkm.lexer import Token
from syncode.larkm.tree import Tree
from syncode.larkm.parsers.lalr_analysis import Reduce
from syncode.larkm.parsers.lalr_parser_state import ParserState


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
        # elif self._pos_map[symbol][-1][0] == start_pos:
        #     self._pos_map[symbol][-1] = pos

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

    def get_symbol_pos(self, symbol:str, idx:int) -> Tuple[int, int]:
        """
        Returns the k-th position of the symbol in the code.
        """
        return self._pos_map[symbol][idx]

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
    
    def _update_symbol_pos_map_terminals(self, lexer_tokens: Iterable[Token], parsed_lexer_tokens: Iterable[Token]):
        """
        Updates the uc_map with the current token for terminals.
        """
        if len(lexer_tokens) > len(parsed_lexer_tokens):
            len_parsed = len(parsed_lexer_tokens)

            # parsed_lexer_tokens does not contain the IGNORED tokens. So, we need to count the number of IGNORED tokens in the parsed_lexer_tokens
            start_idx = 0
            cnt_non_ignore = 0  # Just temporary index to iterate over lexer_tokens

            # This loop should terminate since there are more non-IGNORED tokens in lexer_tokens than in all tokens in parsed_lexer_tokens
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
                    self.add_symbol_pos(
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
                    self.add_symbol_pos(
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
    