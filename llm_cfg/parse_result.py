import copy
from enum import Enum

class RemainderState(Enum):
    """
    The state of the reminder after parsing partial code.
    """
    COMPLETE = 0
    MAYBE_COMPLETE = 1
    INCOMPLETE = 2

class ParseResult:
    """ 
    Stores the result of parsing. 
    """
    def __init__(self, cur_accept_terminals, next_accept_terminals, remainder, remainder_state: RemainderState, next_ac_indents=None):
        self.remainder = remainder
        self.remainder_state = remainder_state # Whether the final_string is a complete terminal
        self.cur_accept_terminals = copy.copy(cur_accept_terminals)
        self.next_accept_terminals = copy.copy(next_accept_terminals) 
        self.next_ac_indents: IndentationConstraint = next_ac_indents

        if remainder_state == RemainderState.INCOMPLETE: # If the terminal is not complete, then next_accept_terminals should be None
            assert len(next_accept_terminals) == 0

    def __repr__(self):
        return 'final_incomplete_str: {}\nis_terminal_complete: {}\ncur_accept_terminals: {}\nnext_accept_terminals: {}\nNext indent:{}'.format(repr(self.remainder), self.remainder_state, self.cur_accept_terminals, self.next_accept_terminals, self.next_ac_indents)
    
    def __eq__(self, other):
        return self.remainder == other.remainder and self.remainder_state == other.remainder_state and self.cur_accept_terminals == other.cur_accept_terminals and self.next_accept_terminals == other.next_accept_terminals and self.next_ac_indents == other.next_ac_indents

class IndentationConstraint:
    """
    Stores the indentation constraints for a terminal.
    """
    def __init__(self, accept_indents=None, greater_than_indent_val=None):
        self.accept_indents = accept_indents
        self.greater_than_indent_val = greater_than_indent_val
        assert accept_indents is None or greater_than_indent_val is None # Exactly one of them should be None

    def __repr__(self):
        return 'accept_indents: {}, greater_than_indent_val: {}'.format(self.accept_indents, self.greater_than_indent_val)

    def __eq__(self, other):
        return self.accept_indents == other.accept_indents and self.greater_than_indent_val == other.greater_than_indent_val
    