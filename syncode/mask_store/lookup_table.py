from collections import defaultdict
import copy
import torch
import regex
from syncode.mask_store.mask_store import JointFSMState
from syncode.parse_result import IndentationConstraint
from typing import Any, Tuple, Iterable, Dict, Union
import logging
logger = logging.getLogger(__name__)


class LookupTable:
    """
    Stores the overapproximate tokens
    """
    def __init__(
            self, 
            vocab: Iterable[str], 
            eos_token_id: int,
            special_token_ids: Iterable[int], 
            indent=False, 
            mode='grammar_mask'
        ):
        self._fsm_state_and_next_terminal_to_tokens: defaultdict = defaultdict(list)
        self._overapprox_lookup: Dict[JointFSMState, Any] = {}
        self._exact_lookup: dict = {}
        self._mode = mode
        self._vocab: Iterable[str] = vocab
        self.indent = indent

        # In the default mask, add all tokens that are special tokens except the EOS token
        self._default_mask: torch.IntTensor = torch.zeros(len(vocab), dtype=torch.bool)
        for token_id in special_token_ids:
            if token_id != eos_token_id:
                self._default_mask[token_id] = 1

        if indent:
            logger.info("Indentation mode enabled")
            self._whitespace_tokens_map: defaultdict = defaultdict(list)
            self._indentation_to_tokens_map: defaultdict = defaultdict(list)
            self._create_indentation_to_tokens_map()

    def incomplete_case_lookup(self, fsm_state: JointFSMState) -> Any:
        assert isinstance(fsm_state, JointFSMState)
        if self._mode == 'grammar_mask':
            return self._overapprox_lookup[fsm_state]
        elif self._mode == 'grammar_strict':
            if fsm_state in self._exact_lookup:
                return self._exact_lookup[fsm_state]
            else:
                return self._overapprox_lookup[fsm_state]
        raise ValueError(f"Invalid mode: {self._mode}")
    
    def store_overapprox_lookup(self, fsm_state: JointFSMState, mask: torch.Tensor):
        assert isinstance(fsm_state, JointFSMState)
        if fsm_state not in self._overapprox_lookup:
            self._overapprox_lookup[fsm_state] = self._get_default_mask()
        self._overapprox_lookup[fsm_state] |= mask
    
    def complete_case_lookup(self, fsm_state: JointFSMState) -> Any:
        assert isinstance(fsm_state, JointFSMState)
        return self._exact_lookup[fsm_state]

    def add_exact_lookup(self, fsm_state: JointFSMState, token):
        assert isinstance(fsm_state, JointFSMState)
        if fsm_state not in self._exact_lookup:
            self._exact_lookup[fsm_state] = []
        self._exact_lookup[fsm_state].append(token)        

    def fsm_state_and_next_terminal_to_tokens(self, fsm_state: JointFSMState, next_terminal) -> torch.Tensor:
        assert isinstance(fsm_state, JointFSMState)
        return self._fsm_state_and_next_terminal_to_tokens[(fsm_state, next_terminal)]

    def fsm_state_and_next_terminal_to_tokens_store(self, fsm_state: JointFSMState, next_terminal, mask: torch.Tensor):
        assert isinstance(fsm_state, JointFSMState)
        self._fsm_state_and_next_terminal_to_tokens[(fsm_state, next_terminal)] = mask
    
    def fsm_state_and_next_terminal_to_tokens_add(self, fsm_state: JointFSMState, next_terminal, token):
        assert isinstance(fsm_state, JointFSMState)
        self._fsm_state_and_next_terminal_to_tokens[(fsm_state, next_terminal)].append(token)

    def _list_to_mask(self, tokens_idx_list) -> torch.Tensor:
        indices = torch.tensor(tokens_idx_list)
        tokens_mask = self._get_default_mask()
        tokens_mask[indices] = 1
        return tokens_mask

    def convert_lookups_from_list_to_mask(self):
        """
        Converts the lookups from list of tokens to boolean tensor mask
        """
        for key, val in self._fsm_state_and_next_terminal_to_tokens.items():
            m = self._list_to_mask(val)
            self._fsm_state_and_next_terminal_to_tokens[key] = m
            (fsm_state, _) = key
            self.store_overapprox_lookup(fsm_state, m)
        
        for key, val in self._exact_lookup.items():
            self._exact_lookup[key] = self._list_to_mask(val)
        
        # TODO: move this logic to the lookup table
        if self.indent:
            for key, val in self._whitespace_tokens_map.items():
                self._whitespace_tokens_map[key] = self._list_to_mask(val)
            for key, val in self._indentation_to_tokens_map.items():
                self._indentation_to_tokens_map[key] = self._list_to_mask(val)

    def _get_default_mask(self) -> torch.Tensor:
        return self._default_mask.clone()

    def _create_indentation_to_tokens_map(self):
        """
        We create a mapping from indentation to overapproximate tokens. This is useful for the indentation rule.
        """
        for token_idx, token in enumerate(self._vocab):
            full_match, indent = self._get_indent_type(token)
            if full_match:
                self._whitespace_tokens_map[indent].append(token_idx)
            else:
                self._indentation_to_tokens_map[indent].append(token_idx)

    def _get_indent_type(self, s: Union[str, bytes]) -> Tuple[bool, int]:
        """
        Determine the indentation type and level from a string or bytes input.
        
        Args:
            s (Union[str, bytes]): The input string or bytes to analyze
            
        Returns:
            Tuple[bool, int]: A tuple containing:
                - bool: Whether the input is entirely whitespace
                - int: The indentation level (spaces + 4*tabs)
        """
        # Convert bytes to string if needed
        if isinstance(s, bytes):
            try:
                s_str = s.decode('utf-8')
            except UnicodeDecodeError:
                # Handle decode errors by returning default values
                return False, 0
        else:
            s_str = s
            
        m = regex.match(r'[\t ]+', s_str, partial=True)
        full_match = False
        if m != None:
            start, end = m.start(), m.end()
            if end == len(s_str):
                full_match = True
            return full_match, s_str[start: end].count(' ') + 4*s_str[start: end].count('\t')
        return False, 0 

    def get_indentation_tokens(self, indent_constraint: IndentationConstraint, get_list=False):
        """
        Returns the tokens mask for the indentation constraint
        """
        out_mask = self._get_default_mask()
        if indent_constraint.greater_than_indent_val is not None:
            for indent in self._indentation_to_tokens_map.keys():
                if indent > indent_constraint.greater_than_indent_val:
                    out_mask |= self._indentation_to_tokens_map[indent]
            
            for indent in self._whitespace_tokens_map.keys():  # We are ok with any num of whitespace
                out_mask |= self._whitespace_tokens_map[indent]

        elif indent_constraint.accept_indents is not None:
            for indent in indent_constraint.accept_indents:
                if indent in self._indentation_to_tokens_map:
                    out_mask |= self._indentation_to_tokens_map[indent]
            
            max_acceptable_indent = max(indent_constraint.accept_indents)
            for indent in self._whitespace_tokens_map.keys():  # We are ok with num whitespace <= largest accepted indent
                if indent <= max_acceptable_indent:
                    out_mask |= self._whitespace_tokens_map[indent]
        
        if get_list: # This is useful for testing
            return self._get_tokens_list(out_mask) 
        return out_mask

    def _get_tokens_list(self, token_mask) -> Iterable[str]:
        return [self._vocab[idx.item()] for idx in torch.where(token_mask == True)[0]]
    