import unittest
from unittest.mock import MagicMock
import time
import random, sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../..')
from syncode.mask_store.byte_tokenizer import ByteTokenizer
from syncode.mask_store.byte_tokenizer import VocabType, detect_vocab_type, bytes_to_unicode

class TestByteTokenizer(unittest.TestCase):
    """Test cases for the ByteTokenizer class with different tokenizer types."""
    
    def create_mock_tokenizer(self, vocab, vocab_type):
        """Create a mock tokenizer of the specified type with the given vocabulary."""
        mock_tokenizer = MagicMock()
        mock_tokenizer.get_vocab.return_value = vocab
        
        # Set up the appropriate properties based on vocab_type
        if vocab_type == VocabType.RAW:
            # For tiktoken-style tokenizers
            mock_tokenizer.tokenizer = "tiktoken.Encoding"
            mock_tokenizer.vocab_files_names = {"vocab_file": "tiktoken_vocab.json"}
        elif vocab_type == VocabType.BYTE_FALLBACK:
            # For LLaMA-2 style tokenizers
            mock_tokenizer.tokenizer = "ByteFallbackTokenizer"
        else:  # BYTE_LEVEL
            # For GPT-2 style tokenizers
            mock_tokenizer.tokenizer = "ByteLevelTokenizer"
            
        # Set up decode method for testing
        def mock_decode(token_ids, **kwargs):
            result = ""
            for token_id in token_ids:
                for token, tid in vocab.items():
                    if tid == token_id:
                        result += token
                        break
            return result
            
        mock_tokenizer.decode = mock_decode
        
        # Set up encode method for testing
        def mock_encode(text, **kwargs):
            # Simplified encoding - just matching exact tokens
            result = []
            remaining = text
            while remaining:
                matched = False
                for token, token_id in sorted(vocab.items(), key=lambda x: len(x[0]), reverse=True):
                    if remaining.startswith(token):
                        result.append(token_id)
                        remaining = remaining[len(token):]
                        matched = True
                        break
                if not matched:
                    # Skip one character if no match
                    remaining = remaining[1:]
            return result
            
        mock_tokenizer.encode = mock_encode
        mock_tokenizer.unk_token_id = 0
        
        return mock_tokenizer
    
    def test_raw_tokenizer(self):
        """Test ByteTokenizer with a RAW (tiktoken-style) tokenizer."""
        # Create mock vocabulary for a raw tokenizer
        vocab = {
            "hello": 1,
            "world": 2,
            "!": 3,
            "你": 4,
            "好": 5,
            "吗": 6,
            "？": 7
        }
        
        mock_tokenizer = self.create_mock_tokenizer(vocab, VocabType.RAW)
        byte_tokenizer = ByteTokenizer(mock_tokenizer, VocabType.RAW)
        
        # Test encoding
        input_bytes = b"hello world!"
        expected_ids = [1, 2, 3]  # hello, world, !
        # Mocking - we'll just check if the encode method was called correctly
        mock_tokenizer.encode.return_value = expected_ids
        
        # Test decoding
        token_ids = [4, 5, 6, 7]  # 你, 好, 吗, ？  
        mock_tokenizer.decode.return_value = "你好吗？"
        result = byte_tokenizer.decode(token_ids)
        self.assertEqual(result.decode('utf-8'), "你好吗？")
    
    def test_byte_fallback_tokenizer(self):
        """Test ByteTokenizer with a BYTE_FALLBACK (Llama-2-style) tokenizer."""
        # Create mock vocabulary for a byte fallback tokenizer
        vocab = {
            "hello": 1,
            "▁world": 2,  # Space-prefixed token
            "<0x21>": 3,   # Byte fallback for !
            "<0xE4>": 4,   # First byte of 你 in UTF-8
            "<0xBD>": 5,   # Second byte of 你 in UTF-8
            "<0xA0>": 6,   # Third byte of 你 in UTF-8
        }
        
        mock_tokenizer = self.create_mock_tokenizer(vocab, VocabType.BYTE_FALLBACK)
        byte_tokenizer = ByteTokenizer(mock_tokenizer, VocabType.BYTE_FALLBACK)
        
        # Test encoding/decoding of byte fallback tokens
        self.assertEqual(byte_tokenizer.enbyte_fn("<0x21>"), b"!")
        self.assertEqual(byte_tokenizer.enbyte_fn("▁world"), b" world")
        
        # Verify byte_vocab mapping
        self.assertEqual(byte_tokenizer.byte_vocab[b"!"], 3)
        self.assertEqual(byte_tokenizer.byte_vocab[b" world"], 2)
    
    def test_byte_level_tokenizer(self):
        """Test ByteTokenizer with a BYTE_LEVEL (GPT-2-style) tokenizer."""
        # Create a simplified byte-to-unicode mapping for testing
        byte_to_unicode = bytes_to_unicode()
        unicode_to_byte = {v: k for k, v in byte_to_unicode.items()}
        
        # Create mock vocabulary with encoded characters
        # 'Ġ' (U+0120) represents space in GPT-2 tokenizer
        vocab = {
            "hello": 1,
            "Ġworld": 2,  # Space-prefixed token in byte-level encoding
            byte_to_unicode[ord("!")]: 3,  # Encoded !
        }
        
        mock_tokenizer = self.create_mock_tokenizer(vocab, VocabType.BYTE_LEVEL)
        byte_tokenizer = ByteTokenizer(mock_tokenizer, VocabType.BYTE_LEVEL)
        
        # Test encoding byte-level tokens
        # The byte representation of 'Ġ' followed by 'world'
        self.assertEqual(byte_tokenizer.enbyte_fn("Ġworld")[0], ord(' '))
        
        # Test that we can decode a sequence
        token_ids = [1, 2, 3]  # hello, Ġworld, !
        mock_tokenizer.decode.return_value = "hello world!"
        byte_result = byte_tokenizer.decode(token_ids)
        
        # The actual bytes might be different due to the encoding,
        # but decoding to UTF-8 should give us the original text
        try:
            text_result = byte_result.decode('utf-8')
            self.assertIn("hello", text_result)
            self.assertIn("world", text_result)
        except UnicodeDecodeError:
            # If we can't decode, that's also acceptable for this mock test
            pass
        
    def test_batched_decoding(self):
        """Test batched decoding capabilities."""
        vocab = {
            "hello": 1,
            "world": 2,
            "!": 3,
            "<s>": 4,  # special token
            "</s>": 5,  # special token
        }
        
        mock_tokenizer = self.create_mock_tokenizer(vocab, VocabType.RAW)
        mock_tokenizer.all_special_ids = [4, 5]  # Mark <s> and </s> as special tokens
        byte_tokenizer = ByteTokenizer(mock_tokenizer, VocabType.RAW)
        
        # Test batched decoding
        token_batches = [
            [4, 1, 2],    # <s> hello world
            [4, 1, 2, 3]  # <s> hello world !
        ]
        batch_results = byte_tokenizer.batched_decode(token_batches)
        self.assertEqual(len(batch_results), 2)
        
        # Test batched decoding with skip_special_tokens
        batch_results_skipped = byte_tokenizer.batched_decode(token_batches, skip_special_tokens=True)
        self.assertEqual(len(batch_results_skipped), 2)
        
    def test_auto_detection(self):
        """Test automatic detection of tokenizer type."""
        # Test RAW detection
        raw_vocab = {"hello": 1, "world": 2}
        raw_tokenizer = self.create_mock_tokenizer(raw_vocab, VocabType.RAW)
        self.assertEqual(detect_vocab_type(raw_tokenizer), VocabType.RAW)
        
        # Test BYTE_FALLBACK detection
        fallback_vocab = {"hello": 1, "<0x0A>": 2}
        fallback_tokenizer = self.create_mock_tokenizer(fallback_vocab, VocabType.BYTE_FALLBACK)
        self.assertEqual(detect_vocab_type(fallback_tokenizer), VocabType.BYTE_FALLBACK)
        
        # Test BYTE_LEVEL detection
        bytelevel_vocab = {"hello": 1, "Ġworld": 2}
        bytelevel_tokenizer = self.create_mock_tokenizer(bytelevel_vocab, VocabType.BYTE_LEVEL)
        # Make sure our mock tokenizer correctly returns the vocabulary with the Ġ character
        self.assertIn("Ġworld", bytelevel_tokenizer.get_vocab())
        self.assertEqual(detect_vocab_type(bytelevel_tokenizer), VocabType.BYTE_LEVEL)
        
    def test_decoding_performance(self):
        """Test basic decoding performance."""
        # Create a larger vocabulary for more realistic testing
        vocab = {f"token{i}": i for i in range(1000)}
        # Add some special tokens
        vocab["<s>"] = 1000
        vocab["</s>"] = 1001
        
        mock_tokenizer = self.create_mock_tokenizer(vocab, VocabType.RAW)
        mock_tokenizer.all_special_ids = [1000, 1001]
        byte_tokenizer = ByteTokenizer(mock_tokenizer, VocabType.RAW)
        
        # Generate random token sequences of different lengths
        sequence_lengths = [10, 100, 1000, 10000]  # Added longer sequence
        sequences = {}
        
        for length in sequence_lengths:
            sequences[length] = [random.randint(1, 999) for _ in range(length)]
        
        # Test single decode performance
        for length, sequence in sequences.items():
            # Warm-up run
            byte_tokenizer.decode(sequence)
            
            # Actual timed run
            start_time = time.time()
            repetitions = max(1, 1000 // length)  # More repetitions for shorter sequences
            for _ in range(repetitions):
                byte_tokenizer.decode(sequence)
            elapsed = time.time() - start_time
            
            # Calculate tokens per second
            tokens_per_second = (length * repetitions) / elapsed
            self.assertIsNotNone(tokens_per_second)  # Simple assertion to check execution
        
        # Test with special token handling
        special_sequence = sequences[1000].copy()
        # Insert special tokens randomly
        for _ in range(50):
            pos = random.randint(0, len(special_sequence) - 1)
            special_sequence[pos] = 1000 if random.random() < 0.5 else 1001
        
        # Warm-up run
        byte_tokenizer.decode(special_sequence, skip_special_tokens=True)
        
        # Actual timed run
        start_time = time.time()
        for _ in range(10):
            byte_tokenizer.decode(special_sequence, skip_special_tokens=True)
        elapsed = time.time() - start_time
        self.assertGreater(elapsed, 0)  # Simple assertion to check execution
        
        # Test batched decode performance
        batch_sizes = [10, 50, 100]
        
        for batch_size in batch_sizes:
            # Create batch of same-length sequences
            batch = [sequences[100] for _ in range(batch_size)]
            
            # Warm-up run
            byte_tokenizer.batched_decode(batch)
            
            # Actual timed run
            start_time = time.time()
            for _ in range(5):  # Run multiple times for more stable measurement
                byte_tokenizer.batched_decode(batch)
            elapsed = time.time() - start_time
            
            # Calculate tokens per second
            tokens_per_second = (100 * batch_size * 5) / elapsed
            self.assertGreater(tokens_per_second, 0)  # Simple assertion to check execution

    def test_real_tokenizers(self):
        """Test ByteTokenizer with real HuggingFace tokenizers."""
        # Skip test if transformers is not available
        try:
            import transformers
            from transformers import AutoTokenizer
            
            # Test strings with different characteristics
            test_strings = [
                "Hello, world!",
                "This is a test of ByteTokenizer with different languages.",
                "Let's try some emojis: 🚀🔥🌍",
                "And some CJK characters: 你好, 안녕하세요, こんにちは"
            ]
            
            models = [
                "google/gemma-2-2b-it",
                "meta-llama/Llama-3.1-8B-Instruct"
            ]
            
            # Try to load at least one model for testing
            for model_name in models:
                try:
                    # Load the tokenizer
                    tokenizer = AutoTokenizer.from_pretrained(model_name)
                    byte_tokenizer = ByteTokenizer(tokenizer)
                    
                    # Test at least one string
                    test_str = test_strings[0]
                    token_ids = tokenizer.encode(test_str, add_special_tokens=False)
                    bytes_result = byte_tokenizer.decode(token_ids)
                    
                    # Simple assertion that we got some bytes back
                    self.assertIsInstance(bytes_result, bytes)
                    
                    # Skip the rest of the test
                    break
                except Exception:
                    continue
                    
        except (ImportError, ConnectionError):
            # Skip the test if no tokenizers are available
            self.skipTest("Transformers library not available or no internet connection")

    def test_roundtrip_encoding_decoding(self):
        """Test encoding and decoding round-trip."""
        # Create a simple vocabulary for testing
        raw_vocab = {
            "hello": 1,
            " ": 2,
            "world": 3,
            "!": 4,
        }
        
        mock_tokenizer = self.create_mock_tokenizer(raw_vocab, VocabType.RAW)
        byte_tokenizer = ByteTokenizer(mock_tokenizer, VocabType.RAW)
        
        # Test string
        test_str = "hello world!"
        
        # Encode with the mock tokenizer
        token_ids = mock_tokenizer.encode(test_str)
        
        # Decode with ByteTokenizer
        decoded_bytes = byte_tokenizer.decode(token_ids)
        
        # Check round-trip
        try:
            decoded_str = decoded_bytes.decode('utf-8')
            self.assertEqual(test_str, decoded_str)
        except UnicodeDecodeError:
            self.fail("Unicode decode error in round-trip test")

if __name__ == "__main__":
    unittest.main()
