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
    def __init__(self, cur_accept_terminals, next_accept_terminals, remainder, remainder_state: RemainderState):
        self.remainder = remainder
        self.remainder_state = remainder_state # Whether the final_string is a complete terminal
        self.cur_accept_terminals = cur_accept_terminals
        self.next_accept_terminals = next_accept_terminals 

        if remainder_state == RemainderState.INCOMPLETE: # If the terminal is not complete, then next_accept_terminals should be None
            assert next_accept_terminals is None 

    def __repr__(self):
        return 'final_incomplete_str: {}\nis_terminal_complete: {}\ncur_accept_terminals: {}\nnext_accept_terminals: {}'.format(repr(self.remainder), self.remainder_state, self.cur_accept_terminals, self.next_accept_terminals)
