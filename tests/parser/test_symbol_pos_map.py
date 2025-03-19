import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../..')
from syncode.parsers.itergen_parser import SymbolPosMap


class TestSymbolPosMap(unittest.TestCase):
    """Test cases for the SymbolPosMap class."""

    def setUp(self):
        """Set up a new SymbolPosMap instance for each test."""
        # Create an empty map for each test
        self.empty_map = SymbolPosMap()
        
        # Create a pre-populated map for read-only tests
        self.sample_map = SymbolPosMap()
        self.sample_map.add_symbol_pos('NUMBER', (0, 2))
        self.sample_map.add_symbol_pos('NUMBER', (4, 6))
        self.sample_map.add_symbol_pos('NUMBER', (8, 10))
        self.sample_map.add_symbol_pos('OPERATOR', (3, 3))
        self.sample_map.add_symbol_pos('OPERATOR', (7, 7))

    def test_add_symbol_pos(self):
        """Test adding a symbol position."""
        # Start with a fresh map for this test
        symbol_map = SymbolPosMap()
        
        # Add the first position for a symbol
        symbol_map.add_symbol_pos('NUMBER', (0, 2))
        self.assertEqual(symbol_map.get_symbol_pos_all('NUMBER'), [(0, 2)])
        
        # Add another position with different start
        symbol_map.add_symbol_pos('NUMBER', (4, 6))
        self.assertEqual(symbol_map.get_symbol_pos_all('NUMBER'), [(0, 2), (4, 6)])
        
        # Try adding a position with same start (should not be added)
        symbol_map.add_symbol_pos('NUMBER', (4, 7))
        self.assertEqual(symbol_map.get_symbol_pos_all('NUMBER'), [(0, 2), (4, 6)])
        
        # Add a position for a new symbol
        symbol_map.add_symbol_pos('IDENTIFIER', (12, 15))
        self.assertEqual(symbol_map.get_symbol_pos('IDENTIFIER', 0), (12, 15))

    def test_get_symbol_pos_start(self):
        """Test getting the start position of a symbol."""
        # Use the pre-populated map for read-only operations
        self.assertEqual(self.sample_map.get_symbol_pos_start('NUMBER', 0), 0)
        self.assertEqual(self.sample_map.get_symbol_pos_start('NUMBER', 1), 4)
        self.assertEqual(self.sample_map.get_symbol_pos_start('OPERATOR', 0), 3)
        
        # Test index out of bounds
        with self.assertRaises(IndexError):
            self.sample_map.get_symbol_pos_start('NUMBER', 5)
            
        # Test non-existent symbol
        with self.assertRaises(IndexError):
            self.sample_map.get_symbol_pos_start('NONEXISTENT', 0)

    def test_get_symbol_pos_end(self):
        """Test getting the end position of a symbol."""
        # Use the pre-populated map for read-only operations
        self.assertEqual(self.sample_map.get_symbol_pos_end('NUMBER', 0), 2)
        self.assertEqual(self.sample_map.get_symbol_pos_end('NUMBER', 2), 10)
        self.assertEqual(self.sample_map.get_symbol_pos_end('OPERATOR', 1), 7)
        
        # Test index out of bounds
        with self.assertRaises(IndexError):
            self.sample_map.get_symbol_pos_end('OPERATOR', 2)

    def test_get_symbol_pos(self):
        """Test getting the full position tuple of a symbol."""
        # Use the pre-populated map for read-only operations
        self.assertEqual(self.sample_map.get_symbol_pos('NUMBER', 0), (0, 2))
        self.assertEqual(self.sample_map.get_symbol_pos('OPERATOR', 1), (7, 7))
        
        # Test index out of bounds
        with self.assertRaises(IndexError):
            self.sample_map.get_symbol_pos('NUMBER', 10)

    def test_get_symbol_pos_all(self):
        """Test getting all positions of a symbol."""
        # Use the pre-populated map for read-only operations
        self.assertEqual(
            self.sample_map.get_symbol_pos_all('NUMBER'), 
            [(0, 2), (4, 6), (8, 10)]
        )
        self.assertEqual(
            self.sample_map.get_symbol_pos_all('OPERATOR'), 
            [(3, 3), (7, 7)]
        )
        
        # Test non-existent symbol returns empty list
        self.assertEqual(self.sample_map.get_symbol_pos_all('NONEXISTENT'), [])

    def test_get_symbol_count(self):
        """Test counting symbols after a position."""
        # Use the pre-populated map for read-only operations
        self.assertEqual(self.sample_map.get_symbol_count('NUMBER'), 3)
        self.assertEqual(self.sample_map.get_symbol_count('NUMBER', after=5), 2)
        self.assertEqual(self.sample_map.get_symbol_count('OPERATOR', after=7), 0)

    def test_crop(self):
        """Test cropping the symbol map at a specific position."""
        # Create a fresh map with known data for this test
        symbol_map = SymbolPosMap()
        symbol_map.add_symbol_pos('NUMBER', (0, 2))
        symbol_map.add_symbol_pos('NUMBER', (4, 6))
        symbol_map.add_symbol_pos('NUMBER', (8, 10))
        symbol_map.add_symbol_pos('OPERATOR', (3, 3))
        symbol_map.add_symbol_pos('OPERATOR', (7, 7))
        
        # First crop: Keep positions ending at or before position 5
        symbol_map.crop(5)
        
        # Verify positions after first crop
        self.assertEqual(
            symbol_map.get_symbol_pos_all('NUMBER'), 
            [(0, 2)]  # Only (0, 2) ends before or at position 5
        )
        self.assertEqual(
            symbol_map.get_symbol_pos_all('OPERATOR'), 
            [(3, 3)]  # Only (3, 3) ends before or at position 5
        )
        
        # Create a new map for second crop test
        symbol_map2 = SymbolPosMap()
        symbol_map2.add_symbol_pos('NUMBER', (0, 2))
        symbol_map2.add_symbol_pos('NUMBER', (4, 6))
        symbol_map2.add_symbol_pos('OPERATOR', (3, 3))
        
        # Second crop: Keep positions ending at or before position 2
        symbol_map2.crop(2)
        
        # Verify positions after second crop
        self.assertEqual(
            symbol_map2.get_symbol_pos_all('NUMBER'), 
            [(0, 2)]  # Only (0, 2) ends before or at position 2
        )
        self.assertEqual(
            symbol_map2.get_symbol_pos_all('OPERATOR'), 
            []  # No operators end before or at position 2
        )

    def test_empty_initialization(self):
        """Test that a new SymbolPosMap is properly initialized empty."""
        self.assertEqual(self.empty_map.get_symbol_pos_all('ANY_SYMBOL'), [])


if __name__ == '__main__':
    unittest.main()
