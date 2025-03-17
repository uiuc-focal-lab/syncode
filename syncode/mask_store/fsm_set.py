import time
import interegular
from typing import Any, Optional, Tuple, Iterable, Dict
from syncode.mask_store.byte_fsm import ByteFSM
import logging
logger = logging.getLogger(__name__)

class JointFSMState:
    """
    Represents the state of the FSM. It consists of the current terminal and the FSM state for the current terminal.
    """
    def __init__(self, terminal, state_id):
        self.terminal = terminal
        self.state_id = state_id

    def __eq__(self, other: 'JointFSMState'):
        return self.terminal == other.terminal and self.state_id == other.state_id

    def __hash__(self):
        return hash((self.terminal, self.state_id))

    def __repr__(self):
        return f"({self.terminal}, {self.state_id})"
    

class FSMSet:
    """
    Stores the FSM for each terminal and provides the method to consume the input string and get the FSM state.
    Uses external ByteFSM for regex matching.
    """
    def __init__(self, terminals: Iterable['MockTerminalDef'], simplifications: Dict[str, str] = {}):
        start_time = time.time()
        self._terminals_to_byte_fsm: Dict[str, ByteFSM] = {}  # Store ByteFSM instances
        self.anything_else = interegular.fsm.anything_else
        self._simplifications: Dict[str, str] = simplifications

        for terminal in terminals:
            if terminal.name in simplifications:
                terminal_regex = simplifications[terminal.name]
            else:
                terminal_regex = terminal.pattern.to_regexp()
            
            # Create a ByteFSM for each terminal pattern
            # This handles the regex pattern matching
            byte_fsm = ByteFSM(terminal_regex)
            self._terminals_to_byte_fsm[terminal.name] = byte_fsm
        logger.info(f"FSMs initialized in {time.time() - start_time:.2f} seconds")

    def states(self):
        """Returns all possible DFA states for all terminals."""
        states = []
        for terminal_name, byte_fsm in self._terminals_to_byte_fsm.items():
            # We need to get states from the ByteFSM's transitions dictionary
            for state_id in byte_fsm.transitions:
                states.append(JointFSMState(terminal_name, state_id))
        return states

    def initial(self, terminal: str):
        """Get the initial state for a specific terminal."""
        return JointFSMState(terminal, self._terminals_to_byte_fsm[terminal].initial)

    def compute_fsm_states(self, input_bytes: bytes) -> Iterable[JointFSMState]:
        """
        Consume input_bytes and get the list of pairs of (terminal, state_id).
        This denotes our current DFA state.
        
        For each terminal's ByteFSM, attempts to consume all input bytes
        and returns state after consumption. A terminal is included only if 
        its FSM can successfully process the entire input.
        
        There is no requirement for the final state to be an accepting state.
        
        Args:
            input_bytes: The input bytes to consume
            
        Returns:
            A list of JointFSMState objects, each containing a terminal and its 
            corresponding state_id after consuming all input bytes.
        """
        dfa_states = []
        
        for terminal, byte_fsm in self._terminals_to_byte_fsm.items():
            # Start from the initial state
            current_state = byte_fsm.initial
            
            # Process input byte by byte
            valid_transition = True
            for byte_val in input_bytes:
                next_state = byte_fsm.get_next_state(current_state, byte_val)
                if next_state is None:
                    valid_transition = False
                    break
                current_state = next_state
            
            # If we were able to process all bytes, add the terminal and final state
            if valid_transition:
                dfa_states.append(JointFSMState(terminal, current_state))
            # Special case for empty input
            elif not input_bytes:
                dfa_states.append(JointFSMState(terminal, byte_fsm.initial))
        
        return dfa_states

    def is_final(self, dfa_state: JointFSMState) -> bool:
        """
        Returns True if the dfa state is a final state
        """
        byte_fsm = self._terminals_to_byte_fsm[dfa_state.terminal]
        return dfa_state.state_id in byte_fsm.finals

    def consume_prefix(self, fsm_state: JointFSMState, input_bytes: bytes) -> Tuple[bool, Optional[bytes]]:
        """
        Consume longest prefix of input_bytes that is accepted by dfa and return the remainder.
        """
        terminal = fsm_state.terminal
        current_state = fsm_state.state_id
        byte_fsm = self._terminals_to_byte_fsm[terminal]
        
        success, remainder = byte_fsm.consume_prefix(input_bytes, current_state)
        return success, remainder
    