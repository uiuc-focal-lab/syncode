import os
import unittest
import time
import torch
import sys
from typing import List, Dict, Any, Tuple, Iterable
import copy
import logging
logger = logging.getLogger(__name__)
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../..')

# Import the actual classes
from syncode.mask_store.mask_store import JointFSMState
from syncode.parse_result import IndentationConstraint
from syncode.mask_store.lookup_table import LookupTable

class TestLookupTable(unittest.TestCase):
    def setUp(self):
        # Create a small vocabulary for basic testing
        self.small_vocab = ["token1", "token2", " ", "\t", "  ", "\t\t", "  token", "\ttoken", "token ", "token\t"]
        self.eos_token_id = 0
        self.special_token_ids = [0, 1]
        
        # Create some FSM states for testing - using actual JointFSMState as defined
        self.state1 = JointFSMState("terminal1", 1)
        self.state2 = JointFSMState("terminal2", 2)
        
        # Create lookup table instance
        self.lookup = LookupTable(
            vocab=self.small_vocab,
            eos_token_id=self.eos_token_id,
            special_token_ids=self.special_token_ids,
            indent=True
        )
        
        # For performance tests, create a larger vocabulary
        self.large_vocab_size = 10000
        self.large_vocab = [f"token{i}" for i in range(self.large_vocab_size)]
        
        # Add some whitespace tokens for indentation testing
        for i in range(50): 
            self.large_vocab.append(" " * i)
            self.large_vocab.append("\t" * i)
            self.large_vocab.append(" " * i + "token")
            self.large_vocab.append("\t" * i + "token")
        
        # Create more FSM states for performance testing
        self.many_states = [JointFSMState(f"terminal{i % 100}", i) for i in range(10000)]
    
    def time_function(self, func_name, func, *args, **kwargs):
        """Helper to time a function execution and log it"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        time_taken = end_time - start_time
        logger.info(f"{func_name} execution time: {time_taken:.6f}s")
        return result, time_taken

    def test_initialization(self):
        """Test initialization of the LookupTable"""
        # Check vocabulary
        self.assertEqual(self.lookup._vocab, self.small_vocab)
        
        # Check default mask
        expected_default_mask = torch.zeros(len(self.small_vocab), dtype=torch.bool)
        expected_default_mask[1] = 1  # Only special token that isn't EOS
        
        self.assertTrue(torch.equal(self.lookup._default_mask, expected_default_mask))
        
        # Check indentation mode
        self.assertTrue(self.lookup.indent)
        
        # Check that the whitespace tokens map was created
        self.assertTrue(isinstance(self.lookup._whitespace_tokens_map, dict))
        
        # Check that the indentation tokens map was created
        self.assertTrue(isinstance(self.lookup._indentation_to_tokens_map, dict))

    def test_add_exact_lookup(self):
        """Test adding tokens to exact lookup"""
        # Add some tokens
        self.lookup.add_exact_lookup(self.state1, 2)  # Add token at index 2
        self.lookup.add_exact_lookup(self.state1, 3)  # Add token at index 3
        self.lookup.add_exact_lookup(self.state2, 4)  # Add token at index 4
        
        # Check that the tokens were added to the exact lookup
        self.assertIn(2, self.lookup._exact_lookup[self.state1])
        self.assertIn(3, self.lookup._exact_lookup[self.state1])
        self.assertIn(4, self.lookup._exact_lookup[self.state2])
        
        # Check that the tokens were not added to the wrong states
        self.assertNotIn(2, self.lookup._exact_lookup.get(self.state2, []))
        self.assertNotIn(4, self.lookup._exact_lookup.get(self.state1, []))

    def test_fsm_state_and_next_terminal(self):
        """Test adding and accessing tokens by FSM state and next terminal"""
        next_terminal1 = "next_terminal1"
        next_terminal2 = "next_terminal2"
        
        # Initialize and add tokens
        self.lookup._fsm_state_and_next_terminal_to_tokens[(self.state1, next_terminal1)] = []
        self.lookup.fsm_state_and_next_terminal_to_tokens_add(self.state1, next_terminal1, 2)
        self.lookup.fsm_state_and_next_terminal_to_tokens_add(self.state1, next_terminal1, 3)
        
        self.lookup._fsm_state_and_next_terminal_to_tokens[(self.state2, next_terminal2)] = []
        self.lookup.fsm_state_and_next_terminal_to_tokens_add(self.state2, next_terminal2, 4)
        
        # Check that the tokens were added correctly
        self.assertIn(2, self.lookup._fsm_state_and_next_terminal_to_tokens[(self.state1, next_terminal1)])
        self.assertIn(3, self.lookup._fsm_state_and_next_terminal_to_tokens[(self.state1, next_terminal1)])
        self.assertIn(4, self.lookup._fsm_state_and_next_terminal_to_tokens[(self.state2, next_terminal2)])
        
        # Convert to masks
        self.lookup.convert_lookups_from_list_to_mask()
        
        # Check that the tokens were converted to masks correctly
        state1_terminal1_mask = self.lookup.fsm_state_and_next_terminal_to_tokens(self.state1, next_terminal1)
        self.assertTrue(state1_terminal1_mask[2])
        self.assertTrue(state1_terminal1_mask[3])
        self.assertFalse(state1_terminal1_mask[4])
        
        state2_terminal2_mask = self.lookup.fsm_state_and_next_terminal_to_tokens(self.state2, next_terminal2)
        self.assertTrue(state2_terminal2_mask[4])
        self.assertFalse(state2_terminal2_mask[2])
        self.assertFalse(state2_terminal2_mask[3])

    def test_overapprox_lookup(self):
        """Test storing and retrieving overapproximate lookups"""
        # Create masks
        mask1 = torch.zeros(len(self.small_vocab), dtype=torch.bool)
        mask1[5] = 1
        mask1[6] = 1
        
        mask2 = torch.zeros(len(self.small_vocab), dtype=torch.bool)
        mask2[7] = 1
        mask2[8] = 1
        
        # Store the masks
        self.lookup.store_overapprox_lookup(self.state1, mask1)
        self.lookup.store_overapprox_lookup(self.state2, mask2)
        
        # Check that the masks were stored correctly
        stored_mask1 = self.lookup.incomplete_case_lookup(self.state1)
        self.assertTrue(stored_mask1[5])
        self.assertTrue(stored_mask1[6])
        
        stored_mask2 = self.lookup.incomplete_case_lookup(self.state2)
        self.assertTrue(stored_mask2[7])
        self.assertTrue(stored_mask2[8])
        
        # Store another mask for state1 and check that it's ORed with the existing mask
        mask1_additional = torch.zeros(len(self.small_vocab), dtype=torch.bool)
        mask1_additional[9] = 1
        
        self.lookup.store_overapprox_lookup(self.state1, mask1_additional)
        
        updated_mask1 = self.lookup.incomplete_case_lookup(self.state1)
        self.assertTrue(updated_mask1[5])
        self.assertTrue(updated_mask1[6])
        self.assertTrue(updated_mask1[9])

    def test_get_indent_type(self):
        """Test the _get_indent_type method"""
        # Test with whitespace-only strings
        self.assertEqual(self.lookup._get_indent_type("    "), (True, 4))  # 4 spaces
        self.assertEqual(self.lookup._get_indent_type("\t\t"), (True, 8))  # 2 tabs (4 spaces each)
        self.assertEqual(self.lookup._get_indent_type("\t  "), (True, 6))  # 1 tab (4 spaces) + 2 spaces
        
        # Test with strings that start with whitespace
        self.assertEqual(self.lookup._get_indent_type("  token"), (False, 2))  # 2 spaces + token
        self.assertEqual(self.lookup._get_indent_type("\ttoken"), (False, 4))  # 1 tab + token
        
        # Test with strings that don't start with whitespace
        self.assertEqual(self.lookup._get_indent_type("token"), (False, 0))
        self.assertEqual(self.lookup._get_indent_type("token  "), (False, 0))

    def test_get_indentation_tokens(self):
        """Test the get_indentation_tokens method"""
        # Create indentation constraints for testing
        constraint1 = IndentationConstraint(greater_than_indent_val=2)
        constraint2 = IndentationConstraint(accept_indents=[2, 4])
        
        # Convert all lookups to masks first
        self.lookup.convert_lookups_from_list_to_mask()
        
        # Test with greater_than_indent_val
        tokens1 = self.lookup.get_indentation_tokens(constraint1, get_list=True)
        
        # Check that tokens with indentation > 2 are included
        # This depends on the specific tokens in the vocabulary, so we'll just check that some tokens are returned
        self.assertTrue(len(tokens1) > 0)
        
        # Test with accept_indents
        tokens2 = self.lookup.get_indentation_tokens(constraint2, get_list=True)
        
        # Check that tokens with indentation in [2, 4] are included
        self.assertTrue(len(tokens2) > 0)
        
        # Check that the tokens returned are valid tokens from the vocabulary
        for token in tokens1:
            self.assertIn(token, self.small_vocab)
        
        for token in tokens2:
            self.assertIn(token, self.small_vocab)

    def test_list_to_mask_conversion(self):
        """Test conversion from token lists to masks"""
        # Add some tokens to the exact lookup
        self.lookup.add_exact_lookup(self.state1, 2)
        self.lookup.add_exact_lookup(self.state1, 3)
        
        # Add some tokens to the fsm_state_and_next_terminal_to_tokens
        next_terminal = "terminal"
        self.lookup._fsm_state_and_next_terminal_to_tokens[(self.state1, next_terminal)] = []
        self.lookup.fsm_state_and_next_terminal_to_tokens_add(self.state1, next_terminal, 4)
        self.lookup.fsm_state_and_next_terminal_to_tokens_add(self.state1, next_terminal, 5)
        
        # Convert to masks
        self.lookup.convert_lookups_from_list_to_mask()
        
        # Check that the tokens were converted to masks correctly
        exact_mask = self.lookup.complete_case_lookup(self.state1)
        self.assertTrue(exact_mask[2])
        self.assertTrue(exact_mask[3])
        self.assertFalse(exact_mask[4])
        self.assertFalse(exact_mask[5])
        
        fsm_mask = self.lookup.fsm_state_and_next_terminal_to_tokens(self.state1, next_terminal)
        self.assertFalse(fsm_mask[2])
        self.assertFalse(fsm_mask[3])
        self.assertTrue(fsm_mask[4])
        self.assertTrue(fsm_mask[5])
        
        # Check that the overapprox lookup was also updated
        overapprox_mask = self.lookup.incomplete_case_lookup(self.state1)
        self.assertTrue(torch.any(overapprox_mask))  # Should have some tokens set

    def test_complete_workflow(self):
        """Test a complete workflow to ensure all components work together"""
        # Add tokens to exact lookup
        self.lookup.add_exact_lookup(self.state1, 2)
        self.lookup.add_exact_lookup(self.state1, 3)
        
        # Add tokens to fsm_state_and_next_terminal_to_tokens
        next_terminal = "terminal"
        self.lookup._fsm_state_and_next_terminal_to_tokens[(self.state1, next_terminal)] = []
        self.lookup.fsm_state_and_next_terminal_to_tokens_add(self.state1, next_terminal, 4)
        
        # Add a mask to overapprox lookup
        mask = torch.zeros(len(self.small_vocab), dtype=torch.bool)
        mask[5] = 1
        self.lookup.store_overapprox_lookup(self.state1, mask)
        
        # Convert to masks
        self.lookup.convert_lookups_from_list_to_mask()
        
        # Check exact lookup
        exact_mask = self.lookup.complete_case_lookup(self.state1)
        self.assertTrue(exact_mask[2])
        self.assertTrue(exact_mask[3])
        
        # Check fsm_state_and_next_terminal_to_tokens
        fsm_mask = self.lookup.fsm_state_and_next_terminal_to_tokens(self.state1, next_terminal)
        self.assertTrue(fsm_mask[4])
        
        # Check overapprox lookup
        overapprox_mask = self.lookup.incomplete_case_lookup(self.state1)
        self.assertTrue(overapprox_mask[5])
        self.assertTrue(torch.any(overapprox_mask & fsm_mask))  # Should share some tokens

    def test_performance_initialization(self):
        """Test the performance of initialization"""
        def initialize_lookup():
            return LookupTable(
                vocab=self.large_vocab,
                eos_token_id=self.eos_token_id,
                special_token_ids=self.special_token_ids,
                indent=True
            )
        
        # Run 5 times to get a reliable measurement
        total_time = 0
        runs = 5
        for i in range(runs):
            _, time_taken = self.time_function(f"Initialization run {i+1}/{runs}", initialize_lookup)
            total_time += time_taken
        
        logger.info(f"Average initialization time ({runs} runs): {total_time/runs:.6f}s")

    def test_performance_token_addition(self):
        """Test the performance of adding tokens - 100x more tokens"""
        # Create an instance for testing
        lookup = LookupTable(
            vocab=self.large_vocab,
            eos_token_id=self.eos_token_id,
            special_token_ids=self.special_token_ids,
            indent=True
        )
        
        def add_tokens():
            # Add 100,000 tokens instead of 1,000
            for i in range(100000):
                state = self.many_states[i % 10000]
                token_id = i % self.large_vocab_size
                lookup.add_exact_lookup(state, token_id)
        
        _, time_taken = self.time_function("Adding 100,000 tokens", add_tokens)

    def test_performance_conversion(self):
        """Test the performance of converting lists to masks - with much more data"""
        # Create an instance for testing
        lookup = LookupTable(
            vocab=self.large_vocab,
            eos_token_id=self.eos_token_id,
            special_token_ids=self.special_token_ids,
            indent=True
        )
        
        # Add many more tokens to the lookup
        logger.info("Preparing for conversion test - adding tokens...")
        token_count = 100000  # 100x more tokens
        for i in range(token_count):
            state = self.many_states[i % 10000]
            token_id = i % self.large_vocab_size
            lookup.add_exact_lookup(state, token_id)
            
            # Also add to fsm_state_and_next_terminal_to_tokens occasionally
            if i % 5 == 0:
                next_terminal = f"terminal{i % 1000}"  # More varied terminals
                if (state, next_terminal) not in lookup._fsm_state_and_next_terminal_to_tokens:
                    lookup._fsm_state_and_next_terminal_to_tokens[(state, next_terminal)] = []
                lookup.fsm_state_and_next_terminal_to_tokens_add(state, next_terminal, token_id)
        
        logger.info(f"Added {token_count} tokens, now converting to masks...")
        
        # Time the conversion
        _, time_taken = self.time_function("Converting large list to masks", lookup.convert_lookups_from_list_to_mask)

    def test_performance_lookup(self):
        """Test the performance of token lookups - with many more lookups"""
        # Create and populate an instance for testing
        lookup = LookupTable(
            vocab=self.large_vocab,
            eos_token_id=self.eos_token_id,
            special_token_ids=self.special_token_ids,
            indent=True
        )
        
        # Add tokens to the lookup - more tokens for a more realistic test
        logger.info("Preparing for lookup test - adding tokens...")
        for i in range(10000):  # 10x more tokens
            state = self.many_states[i % 1000]  # Use 1000 different states
            token_id = i % self.large_vocab_size
            lookup.add_exact_lookup(state, token_id)
        
        # Convert to masks
        lookup.convert_lookups_from_list_to_mask()
        logger.info("Converted to masks, now performing lookups...")
        
        def lookup_tokens():
            results = []
            # Perform many more lookups - 10,000 instead of 100
            num_lookups = 10000
            for i in range(num_lookups):
                state = self.many_states[i % 1000]
                try:
                    results.append(lookup.complete_case_lookup(state))
                except KeyError:
                    pass  # Some states might not have tokens
            return results
        
        _, time_taken = self.time_function(f"Looking up tokens for 10,000 states", lookup_tokens)

    def test_performance_indentation(self):
        """Test the performance of indentation token lookup - with more constraints"""
        # Create an instance for testing
        lookup = LookupTable(
            vocab=self.large_vocab,
            eos_token_id=self.eos_token_id,
            special_token_ids=self.special_token_ids,
            indent=True
        )
        
        # Convert lookups
        lookup.convert_lookups_from_list_to_mask()
        
        def get_indentation_tokens():
            # Create more varied constraints
            constraints = []
            
            # Add greater_than_indent_val constraints
            for i in range(20):  # 4x more constraints
                constraints.append(IndentationConstraint(greater_than_indent_val=i))
            
            # Add accept_indents constraints with various sizes
            for i in range(20):
                # Create accept_indents with different sizes
                constraints.append(IndentationConstraint(accept_indents=list(range(i, i+3))))
                constraints.append(IndentationConstraint(accept_indents=list(range(i, i+5))))
                constraints.append(IndentationConstraint(accept_indents=[i, i+2, i+4, i+6]))
            
            results = []
            # Process each constraint multiple times to simulate repeated lookups
            for _ in range(5):  # 5x repetition
                for constraint in constraints:
                    results.append(lookup.get_indentation_tokens(constraint))
            return results
        
        _, time_taken = self.time_function("Indentation token lookup with 100 constraints, repeated 5 times", get_indentation_tokens)

    def test_performance_overall_workflow(self):
        """Test a complete workflow to measure overall performance - much larger workload"""
        def workflow():
            # Initialize
            lookup = LookupTable(
                vocab=self.large_vocab,
                eos_token_id=self.eos_token_id,
                special_token_ids=self.special_token_ids,
                indent=True
            )
            
            num_tokens = 50000
            logger.info(f"Adding {num_tokens} tokens to various collections...")
            
            for i in range(num_tokens):
                state = self.many_states[i % 10000]
                token_id = i % self.large_vocab_size
                lookup.add_exact_lookup(state, token_id)
                
                # Also add to fsm_state_and_next_terminal_to_tokens
                if i % 5 == 0:
                    next_terminal = f"terminal{i % 1000}"  # More varied terminals
                    if (state, next_terminal) not in lookup._fsm_state_and_next_terminal_to_tokens:
                        lookup._fsm_state_and_next_terminal_to_tokens[(state, next_terminal)] = []
                    lookup.fsm_state_and_next_terminal_to_tokens_add(state, next_terminal, token_id)
                
                # Also add to overapprox lookup occasionally
                if i % 7 == 0:
                    mask = torch.zeros(len(self.large_vocab), dtype=torch.bool)
                    mask[token_id] = 1
                    lookup.store_overapprox_lookup(state, mask)
            
            # Convert lookups
            logger.info("Converting lookups from lists to masks...")
            lookup.convert_lookups_from_list_to_mask()
            
            # Do many more lookups
            logger.info("Performing lookups...")
            results = []
            lookup_count = 1000
            for i in range(lookup_count):
                state = self.many_states[i % 10000]
                try:
                    results.append(lookup.complete_case_lookup(state))
                except KeyError:
                    pass
                
                # Fix for the KeyError issue - use try/except for incomplete_case_lookup as well
                try:
                    results.append(lookup.incomplete_case_lookup(state))
                except KeyError:
                    # If the state doesn't exist in the _overapprox_lookup, just skip it
                    pass
            
            # Check indentation with more constraints
            logger.info("Processing indentation constraints...")
            for i in range(30):
                constraint = IndentationConstraint(greater_than_indent_val=i)
                results.append(lookup.get_indentation_tokens(constraint))
                
                if i < 25:  # Add some accept_indents constraints too
                    constraint = IndentationConstraint(accept_indents=list(range(i, i+5)))
                    results.append(lookup.get_indentation_tokens(constraint))
            
            logger.info("Workflow complete.")
            return results
        
        _, time_taken = self.time_function("Complete large-scale workflow", workflow)


if __name__ == '__main__':
    unittest.main()
