import interegular
from typing import Tuple, Optional, Any, Union

class ByteFSM:
    """
    A finite state machine that operates on bytes rather than characters.
    """
    
    def __init__(self, pattern: str):
        """
        Initialize a ByteFSM from a regular expression pattern.
        
        Args:
            pattern: A regular expression pattern string
        """
        self.pattern = pattern
        
        # Parse the regex pattern and create the character FSM
        regex_fsm = interegular.parse_pattern(pattern).to_fsm()
        
        # Store FSM properties
        self.initial = regex_fsm.initial
        self.finals = set(regex_fsm.finals)
        
        # Get the special "anything_else" marker from interegular
        self.anything_else = interegular.fsm.anything_else
        
        # Create a byte-level alphabet for our FSM
        self.alphabet = {}
        
        # Create transitions dictionary for the byte FSM
        self.transitions = {}
        self.byte_to_category = {}
        
        # Cache for live states to avoid recomputing
        self._live_states_cache = set()
        
        # Build the byte-level transitions from the character-level FSM
        self._build_byte_fsm(regex_fsm)
    
    def _build_byte_fsm(self, regex_fsm):
        """
        Build a byte-level FSM from the character-level FSM.
        
        This method handles the conversion from character transitions to byte transitions,
        properly handling the alphabet categories.
        """
        # Create a new transitions dictionary
        self.transitions = {}
        
        # Create a mapping from byte values to category numbers
        self.byte_to_category = {}
        
        # Extract the mapping from the regex FSM's alphabet and build our byte-level alphabet
        for char, category in regex_fsm.alphabet.items():
            if char == self.anything_else:
                # Keep track of the anything_else category, but don't add to byte mappings
                self.alphabet[self.anything_else] = category
                continue
                
            if isinstance(char, str):
                # Handle string characters
                char_bytes = char.encode('utf-8')
                if len(char_bytes) == 1:
                    # Single byte character - add to our alphabet and mapping
                    byte_val = char_bytes[0]
                    self.alphabet[byte_val] = category
                    self.byte_to_category[byte_val] = category
                else:
                    # Multi-byte characters are handled separately
                    # For now, add the full character to our alphabet
                    self.alphabet[char] = category
            elif isinstance(char, int):
                # Handle integer (byte) characters
                self.alphabet[char] = category
                self.byte_to_category[char] = category
        
        # Make sure all regex FSM states are in our transitions
        for state in regex_fsm.map:
            if state not in self.transitions:
                self.transitions[state] = {}
        
        # Copy the transitions from the regex FSM to our byte FSM
        for state, category_transitions in regex_fsm.map.items():
            for category, target in category_transitions.items():
                if category is None:
                    # Epsilon transition
                    self.transitions[state][None] = target
                else:
                    # Normal transition on a category
                    self.transitions[state][category] = target
        
        # Handle multi-byte Unicode characters separately
        # This is needed because a multi-byte character might need special handling
        for char, category in regex_fsm.alphabet.items():
            if char == self.anything_else or not isinstance(char, str):
                continue
                
            char_bytes = char.encode('utf-8')
            if len(char_bytes) <= 1:
                continue
                
            # For multi-byte characters, we need to add special transitions
            # Make a copy of states to avoid modifying the dictionary during iteration
            states_to_process = list(self.transitions.keys())
            for state in states_to_process:
                if category in self.transitions[state]:
                    target = self.transitions[state][category]
                    
                    # Create intermediate states for the multi-byte character
                    current = state
                    for i, byte in enumerate(char_bytes):
                        if i < len(char_bytes) - 1:
                            next_state = f"{current}_{byte}_{i}_{char}"
                            if next_state not in self.transitions:
                                self.transitions[next_state] = {}
                            self.transitions[current][byte] = next_state
                            current = next_state
                        else:
                            self.transitions[current][byte] = target
    
    def _get_category(self, byte_val: int) -> Any:
        """
        Get the category for a byte value.
        
        Args:
            byte_val: The byte value
            
        Returns:
            The category for the byte value, or the 'anything_else' category if not found
        """
        # Check if we have a specific mapping for this byte
        if byte_val in self.byte_to_category:
            return self.byte_to_category[byte_val]
        
        # If not, return the 'anything_else' category if it exists
        if self.anything_else in self.alphabet:
            return self.alphabet[self.anything_else]
        
        # If there's no 'anything_else', return None (no transition)
        return None
    
    @property
    def num_states(self) -> int:
        """Returns the number of states in the FSM."""
        return len(self.transitions)
    
    @property
    def alphabet_size(self) -> int:
        """Returns the size of the alphabet (unique categories) used in transitions."""
        categories = set()
        for state_transitions in self.transitions.values():
            for category in state_transitions:
                if category is not None:  # Skip epsilon transitions
                    categories.add(category)
        return len(categories)
    
    @property
    def num_transitions(self) -> int:
        """Returns the total number of transitions in the FSM."""
        return sum(len(transitions) for transitions in self.transitions.values())
    
    def get_next_state(self, current: Any, byte_val: int) -> Optional[Any]:
        """
        Get the next state based on the current state and the input byte value.
        
        Args:
            current: The current state
            byte_val: The input byte value
            
        Returns:
            The next state or None if no transition is defined
        """
        if current is None or current not in self.transitions:
            return None
        
        # First check if there's a direct transition on this byte
        if byte_val in self.transitions[current]:
            return self.transitions[current][byte_val]
        
        # If not, get the category for this byte and check if there's a transition on that category
        category = self._get_category(byte_val)
        if category is not None and category in self.transitions[current]:
            return self.transitions[current][category]
        
        return None
    
    def accepts(self, data: Union[str, bytes]) -> bool:
        """
        Check if the FSM accepts the given input data.
        
        Args:
            data: The input string or bytes
            
        Returns:
            True if the FSM accepts the input, False otherwise
        """
        # Convert string to bytes if needed
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Start from the initial state
        current = self.initial
        
        # Process each byte
        for byte in data:
            current = self.get_next_state(current, byte)
            if current is None:
                return False
        
        # Check if the final state is an accepting state
        return current in self.finals
    
    def try_consume_all(self, input_bytes: bytes) -> Optional[Any]:
        """
        Try to consume all input bytes and return the final state reached.
        
        Args:
            input_bytes: The input bytes to consume
            
        Returns:
            The final state reached after consuming all bytes if successful and in a final state,
            otherwise None if any transition is invalid or if not in a final state.
        """
        if not input_bytes:
            # For empty input, check if the initial state is final
            return self.initial if self.initial in self.finals else None
        
        # Start from the initial state
        current = self.initial
        
        # Process each byte
        for byte in input_bytes:
            current = self.get_next_state(current, byte)
            if current is None:
                return None
        
        # Return the final state only if it's an accepting state
        return current if current in self.finals else None
    
    def islive(self, state: Any) -> bool:
        """
        Check if a state is "live", meaning it can potentially reach a final state.
        
        Args:
            state: The state to check
            
        Returns:
            True if the state is live, False otherwise
        """
        # Check cache first
        if state in self._live_states_cache:
            return True
            
        # Final states are always live
        if state in self.finals:
            self._live_states_cache.add(state)
            return True
            
        # Simple BFS to see if we can reach a final state from this state
        visited = set()
        queue = [state]
        
        while queue:
            current = queue.pop(0)
            
            if current in self.finals or current in self._live_states_cache:
                # Update cache for all states in the path
                self._live_states_cache.add(state)
                return True
                
            if current in visited:
                continue
                
            visited.add(current)
            
            # Add all reachable states to the queue
            if current in self.transitions:
                for symbol, next_state in self.transitions[current].items():
                    if next_state not in visited:
                        queue.append(next_state)
        
        return False
        
    def consume_prefix(self, data: Union[str, bytes], current_state: Optional[Any] = None) -> Tuple[bool, Optional[bytes]]:
        """
        Consume longest prefix of data starting from current_state that is accepted by the FSM and return the remainder.
        
        Args:
            data: The input string or bytes
            current_state: The state to start from (defaults to initial state if None)
            
        Returns:
            A tuple (success, remainder) where:
            - success is True if an accept state was reached or if we ended in a live state
            - remainder is the remaining bytes after the consumed prefix, or None if no valid prefix was found
        """
        # Convert to bytes if not already
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Use the provided state or the initial state
        cur_state = self.initial if current_state is None else current_state
        
        longest_accept_index = -1
        if cur_state in self.finals:
            longest_accept_index = 0
            
        for i, byte in enumerate(data):
            # Get category for this byte
            category = self._get_category(byte)
            
            # Check if we have a direct transition on this byte
            if byte in self.transitions.get(cur_state, {}):
                cur_state = self.transitions[cur_state][byte]
            # Check if we have a transition on this category
            elif category is not None and category in self.transitions.get(cur_state, {}):
                cur_state = self.transitions[cur_state][category]
            else:
                # No valid transition - we've reached a "dead" state
                cur_state = None
                break
                
            # Check if we're in a final state
            if cur_state in self.finals:
                longest_accept_index = i + 1
        
        if longest_accept_index != -1:  # Reached accept state at some point
            return True, data[longest_accept_index:]
        elif cur_state is not None and self.islive(cur_state):
            # Reached a live state but never an accept state
            return True, b""
        else:
            # Never reached a final state or ended in a dead state
            return False, None
