import unittest
from typing import Any, Optional, Tuple, Iterable, Dict
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../..')
from syncode.mask_store.fsm_set import FSMSet, JointFSMState

# Mock classes for testing
class MockTerminalDef:
    """Mock version of TerminalDef for testing purposes"""
    def __init__(self, name, pattern):
        self.name = name
        self.pattern = pattern
        
    def __repr__(self):
        return f"TerminalDef({self.name}, {self.pattern})"

class MockRegexPattern:
    """Mock version of RegexPattern for testing purposes"""
    def __init__(self, pattern):
        self.pattern = pattern
        
    def to_regexp(self):
        return self.pattern
        
    def __repr__(self):
        return f"RegexPattern({self.pattern})"


class TestFSMSet(unittest.TestCase):
    def setUp(self):
        # Create some test terminals with different regex patterns
        self.terminals = [
            MockTerminalDef("IDENTIFIER", MockRegexPattern("[a-zA-Z_][a-zA-Z0-9_]*")),
            MockTerminalDef("NUMBER", MockRegexPattern("[0-9]+")),
            MockTerminalDef("STRING", MockRegexPattern('"[^"]*"')),
            MockTerminalDef("WHITESPACE", MockRegexPattern("[ \t\n\r]+")),
            MockTerminalDef("OPERATOR", MockRegexPattern("[+\\-*/=<>!]")),
            MockTerminalDef("KEYWORD", MockRegexPattern("(if|else|while|for|return)")),
            MockTerminalDef("EMOJI", MockRegexPattern("😊+")),  # Test UTF-8 handling
        ]
        
        # Create DFAs instance
        self.dfas = FSMSet(self.terminals)
        
    def test_compute_fsm_states_simple_inputs(self):
        """Test compute_fsm_states with simple inputs matching specific terminals"""
        test_cases = [
            (b"abc123", ["IDENTIFIER"]),
            (b"123", ["NUMBER"]),
            (b'"hello"', ["STRING"]),
            (b"  \t\n", ["WHITESPACE"]),
            (b"+", ["OPERATOR"]),
            (b"if", ["KEYWORD", "IDENTIFIER"]),  # both KEYWORD and IDENTIFIER match 'if'
            ("😊".encode('utf-8'), ["EMOJI"]),
        ]
        
        for input_bytes, expected_terminals in test_cases:
            states = self.dfas.compute_fsm_states(input_bytes)
            terminal_names = [state.terminal for state in states]
            
            # Check that all expected terminals are matched
            for terminal in expected_terminals:
                self.assertIn(terminal, terminal_names, 
                            f"Expected terminal {terminal} to match input '{input_bytes}'")
            
            # Check that no unexpected terminals are matched
            for terminal in terminal_names:
                self.assertIn(terminal, expected_terminals, 
                            f"Unexpected terminal {terminal} matched input '{input_bytes}'")

    def test_compute_fsm_states_state_tracking(self):
        """Test that compute_fsm_states correctly tracks the state of each FSM"""
        # Create a mock ByteFSM with known states for testing
        class MockByteFSM:
            def __init__(self, states, transitions, finals):
                self.states = states
                self.transitions = transitions
                self.finals = finals
                self.initial = states[0]
            
            def get_next_state(self, state, byte_val):
                key = (state, byte_val)
                return self.transitions.get(key, None)
        
        # Create a simple FSM for testing
        states = [0, 1, 2, 3]
        transitions = {
            (0, ord('a')): 1,
            (1, ord('b')): 2,
            (2, ord('c')): 3,
        }
        finals = {3}
        
        # Mock the DFAs object
        original_terminals = self.dfas._terminals_to_byte_fsm.copy()
        self.dfas._terminals_to_byte_fsm = {
            "TEST": MockByteFSM(states, transitions, finals)
        }
        
        try:
            # Test with different inputs
            test_cases = [
                (b"a", 1),    # Should reach state 1
                (b"ab", 2),   # Should reach state 2
                (b"abc", 3),  # Should reach state 3
                (b"", 0),     # Should stay in initial state 0
                (b"x", None), # Should not match and return no states
            ]
            
            for input_bytes, expected_state in test_cases:
                states = self.dfas.compute_fsm_states(input_bytes)
                
                if expected_state is None:
                    self.assertEqual(len(states), 0, 
                                f"Expected no matches for input '{input_bytes}'")
                else:
                    self.assertEqual(len(states), 1, 
                                f"Expected exactly one match for input '{input_bytes}'")
                    self.assertEqual(states[0].terminal, "TEST", 
                                f"Expected 'TEST' terminal for input '{input_bytes}'")
                    self.assertEqual(states[0].state_id, expected_state,  # Changed to state_id
                                f"Expected state {expected_state} for input '{input_bytes}' but got {states[0].state_id}")
        finally:
            # Restore original terminals
            self.dfas._terminals_to_byte_fsm = original_terminals

    def test_consume_prefix(self):
        """Test consume_prefix with various inputs and starting states"""
        test_cases = [
            # (terminal_name, input_bytes, expected_result)
            ("IDENTIFIER", b"abc123 rest", (True, b" rest")),
            ("IDENTIFIER", b"123", (False, None)),  # IDENTIFIER doesn't match digits first
            ("NUMBER", b"123abc", (True, b"abc")),
            ("NUMBER", b"abc", (False, None)),  # NUMBER doesn't match letters
            ("STRING", b'"hello" rest', (True, b" rest")),
            ("STRING", b'hello"', (False, None)),  # STRING needs opening quote
            ("WHITESPACE", b"  \t\nrest", (True, b"rest")),
            ("OPERATOR", b"+rest", (True, b"rest")),
            ("KEYWORD", b"if(x)", (True, b"(x)")),
            ("KEYWORD", b"ifdef", (True, b"def")),  # Matches 'if' and leaves 'def'
            ("EMOJI", "😊😊 text".encode('utf-8'), (True, b" text")),
        ]
        
        for terminal_name, input_bytes, expected_result in test_cases:
            initial_state = self.dfas.initial(terminal_name)
            result = self.dfas.consume_prefix(initial_state, input_bytes)
            self.assertEqual(result, expected_result, 
                            f"Failed for terminal {terminal_name} with input '{input_bytes}'")

    def test_consume_prefix_with_non_initial_states(self):
        """Test consume_prefix starting from non-initial states"""
        # This is a more complex test that requires following transitions
        # For example, for IDENTIFIER after consuming 'a', we'd be in a non-initial state
        
        # First, manually transition to a non-initial state
        terminal_name = "IDENTIFIER"
        byte_fsm = self.dfas._terminals_to_byte_fsm[terminal_name]
        
        # Get the state after consuming 'a'
        next_state = byte_fsm.get_next_state(byte_fsm.initial, ord('a'))
        if next_state is not None:
            non_initial_state = JointFSMState(terminal_name, next_state)
            
            # Now test consume_prefix from this state
            result = self.dfas.consume_prefix(non_initial_state, b"bc123 rest")
            self.assertEqual(result, (True, b" rest"))

    def test_byte_regex_handling(self):
        """Test that byte regex patterns are correctly handled"""
        # This is a more advanced test to ensure UTF-8 encoding is handled correctly
        emoji_terminal = MockTerminalDef("EMOJI_TEST", MockRegexPattern("😊+"))
        dfas = FSMSet([emoji_terminal])
        
        # Test states computation
        states = dfas.compute_fsm_states("😊😊".encode('utf-8'))
        self.assertEqual(len(states), 1)
        self.assertEqual(states[0].terminal, "EMOJI_TEST")
        
        # Test consume_prefix
        initial_state = dfas.initial("EMOJI_TEST")
        result = dfas.consume_prefix(initial_state, "😊😊rest".encode('utf-8'))
        self.assertEqual(result, (True, b"rest"))

    # Specific test for UTF-8 bug
    def test_utf8_bug(self):
        """Test specifically targeting the UTF-8 bug found in the original implementation"""
        # Create a terminal that matches emoji
        emoji_terminal = MockTerminalDef("EMOJI", MockRegexPattern("😊+"))
        dfas = FSMSet([emoji_terminal])
        
        # Test with the emoji pattern
        emoji_initial = dfas.initial("EMOJI")
        result = dfas.consume_prefix(emoji_initial, "😊😊 text".encode('utf-8'))
        print(f"Emoji test: {result}")  # Debug output
        
        # More debug info
        emoji_fsm = dfas._terminals_to_byte_fsm["EMOJI"]
        print(f"ByteFSM states: {len(emoji_fsm.transitions)}")
        print(f"ByteFSM alphabet size: {emoji_fsm.alphabet_size}")
        print(f"ByteFSM transitions: {emoji_fsm.num_transitions}")
        
        # Try using simple patterns too for comparison
        simple_terminal = MockTerminalDef("SIMPLE", MockRegexPattern("a+"))
        simple_dfas = FSMSet([simple_terminal])
        simple_initial = simple_dfas.initial("SIMPLE")
        simple_result = simple_dfas.consume_prefix(simple_initial, b"aaa text")
        print(f"Simple test: {simple_result}")  # Debug output

# Run the tests
if __name__ == "__main__":
    unittest.main(argv=[''], exit=False)
    print("Done running tests")
