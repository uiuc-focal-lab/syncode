import torch
import syncode.common as common
from transformers import LogitsProcessor, PreTrainedTokenizer
from syncode.mask_store.byte_tokenizer import ByteTokenizer
from syncode.parse_result import AcceptSequence, RemainderState
from syncode.parsers.incremental_parser import IncrementalParser, ParseResult
from syncode.parsers import create_parser, create_base_parser
from syncode.mask_store.mask_store import MaskStore
from syncode.parsers.grammars import Grammar
import logging
logger = logging.getLogger(__name__)


# Set to True for debugging
DEBUG = True

class SyncodeLogitsProcessor(LogitsProcessor):
    """
    This class is used to filter the logits of the model to only allow syntactically valid tokens for Python. 

    Args:
        grammar (str): The grammar to use for parsing e.g. "python".
        tokenizer (PreTrainedTokenizer): The tokenizer to use for decoding.
        use_cache (bool, optional): Whether to use the cache. Defaults to True.
        parse_output_only (bool, optional): Whether to parse the prompt. Defaults to False.
        num_samples (int, optional): The number of sequences to generate. Defaults to 1.
        dev_mode (bool, optional): Whether to run in development mode. Defaults to False.
        parser (str, optional): The parser to use. Defaults to 'lalr'.
        mode (str, optional): The mode to use. Defaults to 'grammar_mask'.
    """
    def __init__(self, 
        grammar: Grammar, 
        tokenizer: PreTrainedTokenizer, 
        use_cache=True,
        parse_output_only=True, 
        num_samples=1,
        dev_mode=False,
        parser='lalr',
        mode='grammar_mask'):

        self.tokenizer = tokenizer
        self.byte_tokenizer = ByteTokenizer(tokenizer)

        self.grammar = grammar
        self.dev_mode = dev_mode
        self.batch_size = num_samples
        self.parse_failed = False

        # For backtracking to syntactically valid completions
        self.last_valid_state: list = []
        self.function_ends: list = []

        # We use this when only the LLM output is parsed and not (input+output)
        self.parse_output_only = parse_output_only
        self.start_from = None         

        # Ignore whitespace tokens
        self._ignore_whitespace = self._get_ignore_whitespace(self.grammar)

        # Create parser
        self.inc_parser: IncrementalParser = create_parser(self.grammar, parser=parser, ignore_whitespace=self._ignore_whitespace)

        # Load dfa mask store
        self.dfa_mask_store = MaskStore.init_mask_store(
                                    grammar=self.grammar, 
                                    tokenizer=self.tokenizer, 
                                    use_cache=use_cache, 
                                    mode=mode,
                                    )
        
    
    def _get_ignore_whitespace(self, grammar):
        """
        Check if the grammar allows whitespace tokens to be ignored.
        """
        base_parser = create_base_parser(grammar)
        terminals = base_parser.terminals
        ignore_terminals = base_parser.ignore_tokens
        
        import regex
        ignore_whitespace = False
        for ig_name in ignore_terminals:
            for terminal in terminals:
                if terminal.name == ig_name:
                    if regex.match(terminal.pattern.to_regexp(), ' ') is not None:
                        ignore_whitespace = True # convert to boolean tensor mask. This is useful for fast union operations
        return ignore_whitespace

    def reset(self):
        """
        Resets the decoder state on every new prompt.
        """
        self.last_valid_state = [0 for _ in range(self.batch_size)]
        self.function_ends = [None for _ in range(self.batch_size)]
        self.parse_failed = False
        self.start_from = None
        self.inc_parser.reset()


    def is_valid(self, input_ids: torch.LongTensor, next_token: torch.LongTensor) -> bool:
        """
        Check if the next token is valid given the input_ids.

        Args:
            input_ids (torch.LongTensor): The input ids.
            next_token (torch.LongTensor): The next token.

        Returns:
            bool: True if the next token is valid, False otherwise.
        """
        assert len(input_ids) == 1, "Only one input is supported for now."
        self._set_start_from(input_ids)

        input_ids = torch.cat((input_ids, next_token.unsqueeze(0)), dim=-1)
        partial_code, remainder_bytes = self._get_partial_codes(input_ids)[0]

        res, skip = self._parse_partial_code(
            idx=0, 
            partial_code=partial_code, 
            remainder_bytes=remainder_bytes, 
            accepted_generation=False
            )
        
        if skip: return False
        
        if input_ids[0, -1] == self.tokenizer.eos_token_id:
            # Do not allow the model to generate EOS token until $END in the grammar is reached
            return AcceptSequence(['$END']) in res.accept_sequences
        
        if res.remainder_state == RemainderState.COMPLETE or res.remainder_state == RemainderState.MAYBE_COMPLETE:
            is_valid = True

        # Check if the remainder is a valid prefix for the last terminal
        is_valid = self.dfa_mask_store.is_valid_prefix(res)

        if is_valid:
            self.update_valid_state(partial_code, 0, res)

        return is_valid

    def _set_start_from(self, input_ids):
        if self.start_from is None:
            if self.parse_output_only:
                self.start_from = input_ids.size(1)
            else:
                self.start_from = 0
    

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor) -> torch.FloatTensor:    
        self._set_start_from(input_ids) # start_from is used for choosing where the parsing should start
        partial_codes = self._get_partial_codes(input_ids)

        for idx, (partial_code, remainder_bytes) in enumerate(partial_codes):
            # 1. Parsing
            res, skip = self._parse_partial_code(idx, partial_code, remainder_bytes, accepted_generation=True)
            if skip: continue

            # 2. Computing the accept mask
            accept_mask = self.dfa_mask_store.get_accept_mask(res)

            # 3. Masking the scores
            if torch.sum(accept_mask) != 0: # If there are acceptable tokens for the current partial code 
                if len(scores[idx]) > len(accept_mask):
                    # Pad accept_mask with 0 values. Since scores[i] may be longer than tokenizer vocab size, we need to pad accept_mask with 0 values
                    accept_mask = torch.cat((accept_mask, torch.zeros(len(scores[idx]) - len(accept_mask), dtype=torch.bool)))
                elif len(scores[idx]) < len(accept_mask):
                    accept_mask = accept_mask[: len(scores[idx])]
                scores[idx] = scores[idx].masked_fill(~accept_mask.to(scores.device), -float("inf"))
            else: # Otherwise, report the error and mask no tokens
                logger.debug('No acceptable tokens for the current partial code!')
                logger.debug(repr(res))

        return scores

    def _parse_partial_code(self, idx: int, partial_code: str, remainder_bytes: bytes, accepted_generation=True) -> tuple[ParseResult, bool]:
        """
        Parse the partial code and return the result.
        """
        skip = False
        res = None
        
        try: 
            res = self.inc_parser.get_acceptable_next_terminals(partial_code)

            if len(remainder_bytes) > 0:
                res.remainder_state = RemainderState.INCOMPLETE
                res.remainder = res.remainder.encode('utf-8') + remainder_bytes
            else:
                res.remainder = res.remainder.encode('utf-8')

            self.update_valid_state(partial_code, idx, res)
        except Exception as e:
            if self.dev_mode == True:
                raise e
            elif self.parse_failed == False and accepted_generation:
                self.parse_failed = True
                print("-"*50)
                print(f"Parsing failed! Falling back to unconstrained decoding.\nException: {e}\nPartial code: {partial_code}\nParsed lexical tokens: {self.inc_parser.parsed_lexer_tokens}")
                print("-"*50)
            skip = True
        return res, skip


    def _get_partial_codes(self, input_ids: torch.LongTensor) -> list[(str, bytes)]:
        """
        Get the partial codes for the input_ids and return the remainder bytes if the partial code is not a valid UTF-8 string.
        """     
        output = []
        for idx in range(len(input_ids)):
            if self.parse_output_only:
                partial_code, remainder_bytes = self._bytes_to_string(
                    self.byte_tokenizer.decode(
                        input_ids[idx, self.start_from:].tolist(), skip_special_tokens=True)
                    )
            else:
                partial_code, remainder_bytes = self._bytes_to_string(
                    self.byte_tokenizer.decode(
                        input_ids[idx].tolist(), skip_special_tokens=True)
                    )
            output.append((partial_code, remainder_bytes))
        return output
        

    def update_valid_state(self, partial_code: str, idx: int, r: ParseResult):
        """
        This a simple heuristic to cut off the generated output at the end of the function. 
        TODO: Put this under a flag to enable/disable this heuristic.
        """
        if idx < len(self.function_ends):
            if r.function_end: # If the function end is not None, then the last valid state is the function end
                if self.function_ends[idx] is None: self.function_ends[idx] = []
                self.function_ends[idx].append(len(partial_code) - len(r.remainder))

        if idx < len(self.last_valid_state):
            for accept_seq in r.accept_sequences:
                # 'EOF' is special terminal since $END does not work with python
                if accept_seq[0] == '$END' or accept_seq[0] == 'EOF':
                    self.last_valid_state[idx] = len(partial_code) - len(r.remainder)

    
    @staticmethod
    def _bytes_to_string(byte_sequence: bytes) -> tuple[str, bytes]:
        """
        Convert a byte sequence into a UTF-8 string plus a remainder that is not valid UTF-8.
        
        This function finds the longest valid UTF-8 prefix of the input byte sequence,
        converts it to a Python string, and returns any remaining bytes that couldn't be decoded.
        
        Args:
            byte_sequence: The input byte sequence
            
        Returns:
            A tuple (string, remainder) where:
            - string is the longest valid UTF-8 prefix of the input as a Python string
            - remainder is the rest of the bytes that could not be decoded as UTF-8
            
        Examples:
            >>> bytes_to_string(b'Hello, world!')
            ('Hello, world!', b'')
            >>> bytes_to_string(b'Hello, \xe2\x82\xac!')  # Euro symbol (€) followed by !
            ('Hello, €!', b'')
            >>> bytes_to_string(b'Hello, \xe2\x82!')  # Incomplete Euro symbol
            ('Hello, ', b'\xe2\x82!')
            >>> bytes_to_string(b'\xff\xfe')  # Invalid UTF-8
            ('', b'\xff\xfe')
        """
        if not isinstance(byte_sequence, bytes):
            raise TypeError("Input must be a bytes object")
        
        if not byte_sequence:
            return "", b""
        
        # Try to decode the entire sequence first - common case optimization
        try:
            return byte_sequence.decode('utf-8'), b""
        except UnicodeDecodeError:
            pass
        
        # Find the longest valid prefix by incrementally checking each additional byte
        valid_end = 0
        
        while valid_end < len(byte_sequence):
            try:
                # Try to decode up to the current position
                byte_sequence[:valid_end+1].decode('utf-8')
                valid_end += 1
            except UnicodeDecodeError:
                break
        
        # Return the valid prefix and remainder
        if valid_end > 0:
            return byte_sequence[:valid_end].decode('utf-8'), byte_sequence[valid_end:]
        else:
            return "", byte_sequence
