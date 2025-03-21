import re
import unittest
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../..')
from syncode.mask_store.byte_fsm import ByteFSM

class TestByteFSM(unittest.TestCase):
    """Test suite for the ByteFSM class."""
    
    def test_basic_patterns(self):
        """Test basic regex pattern matching with various inputs."""
        test_patterns = {
            "abc": [
                ("abc", True),
                ("abcd", False),
                ("ab", False)
            ],
            "a[0-9]c": [
                ("a0c", True),
                ("a5c", True),
                ("abc", False),
                ("a12c", False)
            ],
            "a+b*c": [
                ("ac", True),
                ("abc", True),
                ("aac", True),
                ("aabbc", True),
                ("bc", False)
            ],
            "cat|dog": [
                ("cat", True),
                ("dog", True),
                ("bat", False)
            ],
            "hello[0-9]+": [
                ("hello123", True),
                ("hello", False)
            ],
            "(?:(?:(?:\\/\\/[^\n]*|(\r?\n[\t ]*)+))+|/\\*'\\ \\.\\*\\?\\ '\\*/|;)":
            [
                ("//comment", True),
                # ("/*comment*/", True), TODO: this should be fixed in GO grammar
                (";", True),
                ("\n //comment", True),
                ("/*comment", False),
            ],
                "😊": [
                ("😊", True),
                ("a", False)
            ],
        }
        
        for pattern, test_cases in test_patterns.items():
            with self.subTest(pattern=pattern):
                byte_fsm = ByteFSM(pattern)
                re_pattern = re.compile(f"^{pattern}$")
                
                # Log FSM properties for information
                print(f"FSM states: {byte_fsm.num_states}")
                print(f"FSM alphabet size: {byte_fsm.alphabet_size}")
                print(f"FSM transitions: {byte_fsm.num_transitions}")
                
                for test_str, expected in test_cases:
                    with self.subTest(test_str=test_str):
                        # Check Python's re
                        python_match = bool(re_pattern.match(test_str))
                        self.assertEqual(python_match, expected, 
                                       f"Python regex gave unexpected result for pattern '{pattern}' and input '{test_str}'")
                        
                        # Check ByteFSM
                        byte_match = byte_fsm.accepts(test_str)
                        self.assertEqual(byte_match, expected, 
                                       f"ByteFSM gave unexpected result for pattern '{pattern}' and input '{test_str}'")
    
    def test_consume_prefix(self):
        """Test the consume_prefix functionality for various regex patterns."""
        prefix_test_cases = [
            ("abc[0-9]+", [
                ("abc123def", (True, b"def")),
                ("abc", (True, b"")),  # Live state
                ("xyz", (False, None)),
                ("abc123", (True, b"")),
                ("abc123456xyz", (True, b"xyz")),
                ("ab", (True, b""))  # Live state
            ]),
            ("a+b*c", [
                ("acdef", (True, b"def")),
                ("abbcxyz", (True, b"xyz")),
                ("aaabcdef", (True, b"def")),
                ("def", (False, None)),
                ("a", (True, b"")),  # Live state
                ("ab", (True, b"")),  # Live state
                ("aaaabc", (True, b""))
            ]),
            ("cat|dog", [
                ("caterpillar", (True, b"erpillar")),
                ("doghouse", (True, b"house")),
                ("catalog", (True, b"alog")),
                ("ca", (True, b"")),  # Live state
                ("donut", (False, None)),
                ("mouse", (False, None))
            ]),
            ("ab?c", [
                ("abcdef", (True, b"def")),
                ("acxyz", (True, b"xyz")),
                ("abc", (True, b"")),
                ("ac", (True, b"")),
                ("abd", (False, None))
            ]),
            ("😊+", [
                ("😊hello", (True, b"hello")),
                ("😊😊world", (True, b"world")),
                ("hello😊", (False, None)),
                ("😊", (True, b""))
            ]),
            ("[a-z]+@[a-z]+\\.(com|org)", [
                ("user@example.com/page", (True, b"/page")),
                ("admin@site.org?query=1", (True, b"?query=1")),
                ("user@example.net", (False, None)),
                ("user@", (True, b"")),  # Live state
                ("invalid", (True, b""))  # Live state for [a-z]+
            ]),
            ('"[^"”“]+"', [
                ('\"key”', (False, None)),
            ])
        ]
        
        for pattern, test_cases in prefix_test_cases:
            with self.subTest(pattern=pattern):
                byte_fsm = ByteFSM(pattern)
                
                for test_str, expected in test_cases:
                    with self.subTest(test_str=test_str):
                        success, remainder = byte_fsm.consume_prefix(test_str)
                        
                        self.assertEqual(success, expected[0], 
                                       f"Success flag incorrect for pattern '{pattern}' and input '{test_str}'")
                        self.assertEqual(remainder, expected[1], 
                                       f"Remainder incorrect for pattern '{pattern}' and input '{test_str}'")

    
    def test_identifier_regex(self):
        """Test that the identifier regex pattern '[a-zA-Z_][a-zA-Z0-9_]*' works with ByteFSM."""
        # Create a ByteFSM for the identifier pattern
        identifier_fsm = ByteFSM(r'[a-zA-Z_][a-zA-Z0-9_]*')
        
        # Test with valid identifiers
        valid_identifiers = [b'abc', b'x', b'_var', b'abc123', b'ABC_123']
        for ident in valid_identifiers:
            with self.subTest(identifier=ident):
                self.assertTrue(identifier_fsm.accepts(ident), f"Failed to accept valid identifier: {ident}")
                final_state = identifier_fsm.try_consume_all(ident)
                self.assertIsNotNone(final_state, f"Failed to match valid identifier: {ident}")
        
        # Test with invalid identifiers
        invalid_identifiers = [b'123abc', b' abc', b'']
        for ident in invalid_identifiers:
            with self.subTest(identifier=ident):
                self.assertFalse(identifier_fsm.accepts(ident), f"Incorrectly accepted invalid identifier: {ident}")
                final_state = identifier_fsm.try_consume_all(ident)
                self.assertIsNone(final_state, f"Incorrectly matched invalid identifier: {ident}")
    
    def test_fsm_properties(self):
        """Test that FSM properties return valid values."""
        test_patterns = ["abc", "a[0-9]c", "a+b*c", "cat|dog", "😊", "hello[0-9]+"]
        
        for pattern in test_patterns:
            with self.subTest(pattern=pattern):
                byte_fsm = ByteFSM(pattern)
                
                self.assertGreater(byte_fsm.num_states, 0, 
                                 f"FSM for '{pattern}' should have at least one state")
                self.assertGreater(byte_fsm.alphabet_size, 0, 
                                 f"FSM for '{pattern}' should have a non-empty alphabet")
                self.assertGreater(byte_fsm.num_transitions, 0, 
                                 f"FSM for '{pattern}' should have at least one transition")

if __name__ == "__main__":
    unittest.main()
    