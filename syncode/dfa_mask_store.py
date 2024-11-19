from collections import defaultdict
import copy, os, pickle
import interegular
import torch
import regex
import syncode.common as common
from tqdm import tqdm
from syncode.parsers import create_base_parser
from syncode.larkm.lexer import TerminalDef
from syncode.parse_result import IndentationConstraint, RemainderState, ParseResult
from syncode.parsers.grammars.grammar import Grammar
from typing import Any, Optional, Tuple, Iterable, Dict


class DFAState:
    """
    Represents the state of the DFA. It consists of the current terminal and the DFA state for the current terminal.
    """
    def __init__(self, terminal, state_id):
        self.terminal = terminal
        self.state_id = state_id

    def __eq__(self, other: 'DFAState'):
        return self.terminal == other.terminal and self.state_id == other.state_id

    def __hash__(self):
        return hash((self.terminal, self.state_id))

    def __repr__(self):
        return f"({self.terminal}, {self.state_id})"
    

class DFAs:
    """
    Stores the DFAs for each terminal and provides the method to consume the input string and get the DFA state.
    """
    def __init__(self, terminals: Iterable[TerminalDef], simplifications: Dict[str, str] = {}):
        self._terminals_to_dfa: Dict[str, interegular.FSM] = {}
        self.anything_else = interegular.fsm.anything_else # This is special character used for the 
        self._simplifications: Dict[str, str] = simplifications

        for terminal in terminals:
            if terminal.name in simplifications:
                terminal_regex = simplifications[terminal.name]
            else:
                terminal_regex = terminal.pattern.to_regexp()
            # We store the DFA for each terminal (with name as the key) in the dictionary
            self._terminals_to_dfa[terminal.name] = interegular.parse_pattern(terminal_regex).to_fsm()

    def states(self):
        return [DFAState(terminal_name, state_id) for terminal_name, dfa in self._terminals_to_dfa.items() for state_id in dfa.states]

    def initial(self, terminal: str):
        return DFAState(terminal, self._terminals_to_dfa[terminal].initial)

    def compute_dfa_states(self, input_str: str) -> Iterable[DFAState]:
        """
        consume input_str and get the list of pairs of (terminal, dfa_state). This denotes our current DFA state.

        NOTE: The returned DFA state is always a live state
        """
        dfa_states = []
        for (terminal, dfa) in self._terminals_to_dfa.items():
            state_id = self._consume_input(dfa, input_str)
            if state_id is not None:
                dfa_states.append(DFAState(terminal, state_id)) 
        return dfa_states

    def _consume_input(self, dfa: interegular.FSM, input_str: str) -> Optional[int]:
        """
        Conumses the input string and returns the final state if it is live, otherwise returns None
        """
        state_id = dfa.initial
        for i, symbol in enumerate(input_str):
            if not symbol in dfa.alphabet:
                if not self.anything_else in dfa.alphabet:
                    return None
                symbol = self.anything_else

            # Missing transition = transition to dead state
            if not (state_id in dfa.map and dfa.alphabet[symbol] in dfa.map[state_id]):
                return None
            state_id = dfa.map[state_id][dfa.alphabet[symbol]]      
        return state_id

    def is_final(self, dfa_state: DFAState) -> bool:
        """
        Returns True if the dfa state is a final state
        """
        return dfa_state.state_id in self._terminals_to_dfa[dfa_state.terminal].finals

    def consume_prefix(self, dfa_state: DFAState, input_str: str) -> Tuple[bool, Optional[str]]:
        """
        Consume longest prefix of input_str that is accepted by dfa and return the remainder. 
        If we reach a dead state, return (False, None). 
        If the consumption ends at any live state that is not an accept state, return (True, '').
        If we reach a final state, return (True, remainder).
        """
        cur_state_id = dfa_state.state_id
        dfa: interegular.FSM = self._terminals_to_dfa[dfa_state.terminal]

        longest_accept_index = -1

        if cur_state_id in dfa.finals:
            longest_accept_index = 0

        for i, symbol in enumerate(input_str):
            if not symbol in dfa.alphabet:
                if not self.anything_else in dfa.alphabet:
                    cur_state_id = None
                    break
                symbol = self.anything_else

            # Missing transition = transition to dead state
            if not (cur_state_id in dfa.map and dfa.alphabet[symbol] in dfa.map[cur_state_id]):
                cur_state_id = None
                break

            cur_state_id = dfa.map[cur_state_id][dfa.alphabet[symbol]]

            if cur_state_id in dfa.finals:
                longest_accept_index = i+1
        
        if longest_accept_index != -1: # reached accept state at some point
            return (True, input_str[longest_accept_index:])
        elif cur_state_id != None and dfa.islive(cur_state_id): # if state is a live state
            return (True, '')
        
        # if we never reach a final state and reach a dead state at some point
        return (False, None)

class LookupTable:
    """
    Stores the overapproximate tokens
    """
    def __init__(self, vocab: Iterable[str], special_token_ids: Iterable[int], indentation=False, mode='grammar_mask'):
        self._dfa_state_and_next_terminal_to_tokens: defaultdict = defaultdict(list)
        self._overapprox_lookup: Dict[DFAState, Any] = {}
        self._exact_lookup: dict = {}
        self._mode = mode
        self._vocab: Iterable[str] = vocab
        self.indentation = indentation

        self._default_mask = self._get_default_mask(special_token_ids)
        if indentation:
            self._whitespace_tokens_map: defaultdict = defaultdict(list)
            self._indentation_to_tokens_map: defaultdict = defaultdict(list)
            self._create_indentation_to_tokens_map()

    def incomplete_case_lookup(self, dfa_state: DFAState) -> Any:
        assert isinstance(dfa_state, DFAState)
        if self._mode == 'grammar_mask':
            return self._overapprox_lookup[dfa_state]
        elif self._mode == 'grammar_strict':
            if dfa_state in self._exact_lookup:
                return self._exact_lookup[dfa_state]
            else:
                print(f"Warning: Exact lookup not found for {dfa_state} in the DFA mask store. This could be an error.", flush=True) 
                return self._overapprox_lookup[dfa_state]
        raise ValueError(f"Invalid mode: {self._mode}")
    
    def store_overapprox_lookup(self, dfa_state: DFAState, mask: torch.Tensor):
        assert isinstance(dfa_state, DFAState)
        if dfa_state not in self._overapprox_lookup:
            self._overapprox_lookup[dfa_state] = self._get_default_mask()
        self._overapprox_lookup[dfa_state] |= mask
    
    def complete_case_lookup(self, dfa_state: DFAState) -> Any:
        assert isinstance(dfa_state, DFAState)
        if dfa_state not in self._exact_lookup:
            # FIXME: This is bit strange and need to be checked more carefully
            return self._overapprox_lookup[dfa_state]
        return self._exact_lookup[dfa_state]

    def add_exact_lookup(self, dfa_state: DFAState, token):
        assert isinstance(dfa_state, DFAState)
        if dfa_state not in self._exact_lookup:
            self._exact_lookup[dfa_state] = []
        self._exact_lookup[dfa_state].append(token)        

    def dfa_state_and_next_terminal_to_tokens(self, dfa_state: DFAState, next_terminal) -> torch.Tensor:
        assert isinstance(dfa_state, DFAState)
        return self._dfa_state_and_next_terminal_to_tokens[(dfa_state, next_terminal)]

    def dfa_state_and_next_terminal_to_tokens_store(self, dfa_state: DFAState, next_terminal, mask: torch.Tensor):
        assert isinstance(dfa_state, DFAState)
        self._dfa_state_and_next_terminal_to_tokens[(dfa_state, next_terminal)] = mask
    
    def dfa_state_and_next_terminal_to_tokens_add(self, dfa_state: DFAState, next_terminal, token):
        assert isinstance(dfa_state, DFAState)
        self._dfa_state_and_next_terminal_to_tokens[(dfa_state, next_terminal)].append(token)

    def _list_to_mask(self, tokens_idx_list) -> torch.Tensor:
        indices = torch.tensor(tokens_idx_list)
        tokens_mask = self._get_default_mask()
        tokens_mask[indices] = 1
        return tokens_mask

    def convert_lookups_from_list_to_mask(self):
        """
        Converts the lookups from list of tokens to boolean tensor mask
        """
        for key, val in self._dfa_state_and_next_terminal_to_tokens.items():
            m = self._list_to_mask(val)
            self._dfa_state_and_next_terminal_to_tokens[key] = m
            (dfa_state, _) = key
            self.store_overapprox_lookup(dfa_state, m)
        
        for key, val in self._exact_lookup.items():
            self._exact_lookup[key] = self._list_to_mask(val)
        
        # TODO: move this logic to the lookup table
        if self.indentation:
            for key, val in self._whitespace_tokens_map.items():
                self._whitespace_tokens_map[key] = self._list_to_mask(val)
            for key, val in self._indentation_to_tokens_map.items():
                self._indentation_to_tokens_map[key] = self._list_to_mask(val)

    def _get_default_mask(self, special_token_ids=None) -> torch.Tensor:
        if special_token_ids is not None:
            mask = torch.zeros(len(self._vocab), dtype=torch.bool)
        else:
            mask = copy.deepcopy(self._default_mask)
        return mask

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

    def _get_indent_type(self, s: str) -> Tuple[bool, int]:
        m = regex.match(r'[\t ]+', s, partial=True)
        full_match = False
        if m != None:
            start, end = m.start(), m.end()
            if end == len(s):
                full_match = True
            return full_match, s[start: end].count(' ') + 4*s[start: end].count('\t')
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
    

class DFAMaskStore:
    """
    We build an DFA that consists of DFAs for each terminal. We simulate the DFA by consuming the input string for each terminal DFA.

    There are 3 possible cases for the remainder string:

    1. COMPLETE: In this case, the last token is complete (and cannot be further extended) and we know the type of next terminal. Thus, we need to compute all tokens such that consuming the token leads to a live state for the terminal DFA or it reaches a final state for the terminal DFA.

    2. INCOMPLETE: In this case, the remainder is incomplete and does not match any terminal regex. Thus, we need to compute all tokens such that consuming the token leads to a live state for the current terminal DFA or again it reaches a final state for the current terminal DFA at some point.

    3. MAYBE_COMPLETE: In this case the remainder matches a type of terminal. It may happen that we add to the same matched part of the remainder. In that case, there are two possibilities. i) the matched terminal type does not change and thus we can use the next terminal set computed by assuming that. ii) the matched terminal type changes and then we do not know the next terminal set. Thus, we need to compute all tokens such that consuming the token leads to a live state for the current terminal DFA or again it reaches a final state for the current terminal DFA at some point.
    """
    def __init__(self, 
                 terminals: Iterable[TerminalDef], 
                 vocab: Iterable[str], 
                 simplifications: dict={}, 
                 special_token_ids: Iterable=[], 
                 indentation: bool=True,
                 mode='grammar_strict', # 'grammar_strict' or 'grammar_mask'
                 ignore_terminals: Iterable[str]=[]
                 ):
        self._vocab = vocab
        self.special_token_ids = special_token_ids  
        self._mode = mode
        self._dfas = DFAs(terminals, simplifications)

        # Check if whitespace is in ignore terminals
        self._ignore_whitespace = self.set_ignore_whitespace(terminals, ignore_terminals)
        print(f"Ignore whitespace tokens is {self._ignore_whitespace}", flush=True)
        
        # Iterate through each pair of DFA state and next terminals and store the overapproximate tokens
        self._lookup_table = LookupTable(vocab, special_token_ids, indentation=indentation, mode=mode)
        terminal_names = [terminal.name for terminal in terminals]
        self._store_overapproximate_tokens(terminal_names, vocab)

        self.indentation = indentation       

        # NOTE: This should be called at the end of the constructor
        self._lookup_table.convert_lookups_from_list_to_mask() 

    def set_ignore_whitespace(self, terminals: Iterable[TerminalDef], ignore_terminals: Iterable[str]) -> bool:
        ignore_whitespace = False
        for ig_name in ignore_terminals:
            for terminal in terminals:
                if terminal.name == ig_name:
                    if regex.match(terminal.pattern.to_regexp(), ' ') is not None:
                        ignore_whitespace = True # convert to boolean tensor mask. This is useful for fast union operations
        return ignore_whitespace

    @staticmethod
    def load_dfa_mask_store(grammar: Grammar, tokenizer, use_cache=True, logger=common.EmptyLogger(), mode='grammar_strict'):
        '''
        Loads the dfa for the given language and tokenizer. If the dfa is not cached, it is created and cached. 
        '''
        tokenizer_name = type(tokenizer).__name__
        dfa_dir = common.SYNCODE_CACHE + 'mask_stores/' + tokenizer_name + '/'
        grammar_hash = grammar.hash()

        # TODO: Hashing using the tokenizer vocab size, this may be problmatic if we have two fine-tuned models with same tokenizer, same vocab size but different vocab
        dfa_path = f'{dfa_dir}{mode}_{grammar_hash}_{tokenizer.vocab_size}.pkl'
        
        if use_cache and os.path.exists(dfa_path):
            try:
                mask_store = pickle.load(open(dfa_path, 'rb'))
                return mask_store
            except: # If we cannot load the file, we will create the dfa from scratch
                pass
    
        print(f"Creating DFA mask store for {tokenizer_name} and {grammar}, may take more than 10 minutes. Caching at {os.path.abspath(dfa_path)}.", flush=True)
        vocab = common.get_vocab_from_tokenizer(tokenizer)

        base_parser = create_base_parser(grammar)

        simplifications = grammar.simplifications()
        os.makedirs(dfa_dir, exist_ok=True)

        mask_store = DFAMaskStore(base_parser.terminals, vocab, simplifications=simplifications, special_token_ids=[tokenizer.eos_token_id], mode=mode, ignore_terminals=base_parser.ignore_tokens)

        pickle.dump(mask_store, open(dfa_path, 'wb'))
        return mask_store

    def _get_default_mask(self) -> torch.Tensor:
        mask = torch.zeros(len(self._vocab), dtype=torch.bool)
        return mask

    def _store_overapproximate_tokens(self, terminals: Iterable[str], vocab: Iterable[str]):
        """
        Stores the overapproximate tokens for each dfa state and next terminals
        """
        all_dfa_states = self._dfas.states()
        pbar = tqdm(total=len(all_dfa_states))
        for dfa_state in all_dfa_states:
            for token_idx, token in enumerate(vocab):
                is_special_token = token_idx in self.special_token_ids

                if is_special_token:
                    if self._dfas.is_final(dfa_state):
                        self._lookup_table.dfa_state_and_next_terminal_to_tokens_add(
                            dfa_state, '$END', token_idx)
                else:
                    self._process_regular_tokens(terminals, dfa_state, token_idx, token)
            
            pbar.update(1)

    def _process_regular_tokens(self, terminals, dfa_state, token_idx, token):
        remainder = token.replace('\t', '    ')
        is_valid, remainder = self._dfas.consume_prefix(dfa_state, remainder)
        if is_valid:
            if remainder == '':
                # We reached a live state for the current terminal, thus we add the token in all overapproximate sets of next terminals
                for next_terminal in terminals:
                    self._lookup_table.dfa_state_and_next_terminal_to_tokens_add(dfa_state, next_terminal, token_idx)
            else:
                remainder = self.remove_left_whitespace(dfa_state, remainder)

                # We reached the final state while consuming the token, thus we conusme the remainder with all next terminals
                for next_terminal in terminals:
                    initial_state = self._dfas.initial(next_terminal)
                    is_valid, remainder_new = self._dfas.consume_prefix(initial_state, remainder)
                    if self._mode == 'grammar_mask':
                        if is_valid: # In the non-strict mode we overapproximate
                            # We reached a live state for the next terminal, thus we add the 
                            # token in the  overapproximate sets of next terminals
                            self._lookup_table.dfa_state_and_next_terminal_to_tokens_add(dfa_state, next_terminal, token_idx)
                    elif self._mode == 'grammar_strict':
                        if is_valid and remainder_new == '': 
                            # We reached a live state for the next terminal and the remainder 
                            # is empty, thus we add the token in the exact set of next terminals
                            self._lookup_table.dfa_state_and_next_terminal_to_tokens_add(dfa_state, next_terminal, token_idx)
                    else:
                        raise ValueError(f"Invalid mode: {self._mode}")
                    
        # For COMPLETE case:
        remainder = token
        remainder = self.remove_left_whitespace(dfa_state, remainder)

        is_valid, remainder = self._dfas.consume_prefix(dfa_state, remainder)
        if is_valid and remainder == '':
            self._lookup_table.add_exact_lookup(dfa_state, token_idx)

    def remove_left_whitespace(self, dfa_state, remainder):
        """
        Ignore left space at the start of the terminal. This only helps the efficiency
        e.g. without this say if the model wants to generate ' def' then syncode will force it to generate ' ' and 'def' seperately
        """
        if self._dfas.initial(dfa_state.terminal) == dfa_state and remainder.startswith(' ') and self._ignore_whitespace: 
            
            remainder = remainder[1:]
        return remainder
      

    def _lookup_next_tokens_for_dfa_state(self, dfa_state: DFAState, next_terminal) -> torch.Tensor:
        tokens = self._lookup_table.dfa_state_and_next_terminal_to_tokens(dfa_state, next_terminal)
        if tokens == []:
            # TODO: This is a hack. Do something better
            return self._get_default_mask()
        return tokens

    def _lookup_next_tokens(self, dfa_states: Iterable[DFAState], r: ParseResult) -> torch.Tensor:
        overapprox_token_ids = self._get_default_mask()

        # Case when the final string may be incomplete
        for dfa_state in dfa_states:
                for accept_sequence in r.accept_sequences:
                    if dfa_state.terminal != accept_sequence[0]:
                        continue

                    if r.remainder_state == RemainderState.COMPLETE:
                            assert len(accept_sequence) == 1 # Since we only store length 1 accept sequences in this case
                            overapprox_token_ids |= self._lookup_table.complete_case_lookup(dfa_state)

                    if r.remainder_state == RemainderState.INCOMPLETE:
                            overapprox_token_ids |= self._lookup_table.incomplete_case_lookup(dfa_state)
                    
                    if r.remainder_state == RemainderState.MAYBE_COMPLETE:
                            if len(accept_sequence) == 1:
                                overapprox_token_ids |= self._lookup_table.complete_case_lookup(dfa_state)
                            elif len(accept_sequence) == 2:
                                overapprox_token_ids |= self._lookup_next_tokens_for_dfa_state(dfa_state, accept_sequence[1])
                            elif len(accept_sequence) == 3:
                                # This is useful in under-approximating `grammar_strict` mode as they help improve the precision of SynCode
                                if self._mode == 'grammar_strict':
                                    # If the DFA state is a final state we can jump to the start of next terminal
                                    if self._dfas.is_final(dfa_state): 
                                        ignore_init_state = self._dfas.initial(accept_sequence[1])
                                        overapprox_token_ids |= self._lookup_next_tokens_for_dfa_state(ignore_init_state, accept_sequence[2])
                            else:
                                raise ValueError(f"Invalid accept sequence: {accept_sequence}")
        return overapprox_token_ids

    def get_dfa_states(self, r: ParseResult) -> Iterable[DFAState]:
        """
        Returns the DFA state for the current partial code
        """
        cur_incomplete_string = r.remainder
        if cur_incomplete_string is None:
            return []

        cur_dfa_states = self._dfas.compute_dfa_states(cur_incomplete_string)
        return cur_dfa_states

    def get_accept_mask(
            self, 
            r: ParseResult, 
            get_list=False, 
            logger: common.Logger=common.EmptyLogger()
            ) -> torch.Tensor:
        """
        Returns the mask for the acceptable tokens for the current partial code

        Args:
            r (ParseResult): The parse result
            get_list (bool, optional): If True, returns the list of tokens instead of the mask. Defaults to False.
            logger (common.Logger, optional): The logger. Defaults to common.EmptyLogger().
        """
        cur_incomplete_string = r.remainder
        if cur_incomplete_string is None:
            return torch.ones(len(self._vocab), dtype=torch.bool)

        cur_dfa_states = self._dfas.compute_dfa_states(cur_incomplete_string)
        accept_token_mask = self._lookup_next_tokens(cur_dfa_states, r)

        if self.indentation and r.next_ac_indents is not None:
            indent_ac_token = self._lookup_table.get_indentation_tokens(r.next_ac_indents)
            accept_token_mask &= indent_ac_token
            
        if get_list: # This is useful for testing
            return self._get_tokens_list(accept_token_mask)
        return accept_token_mask
    
    def is_valid_prefix(self, r: ParseResult) -> bool:
        """
        Check if r.remainder is a valid prefix for accept sequences in r
        """
        cur_incomplete_string = r.remainder

        cur_dfa_states = self._dfas.compute_dfa_states(cur_incomplete_string)
        for accept_sequence in r.accept_sequences:
            for dfa_state in cur_dfa_states:
                if dfa_state.terminal == accept_sequence[0]:
                    return True
        return False

    def _list_to_mask(self, tokens_idx_list) -> torch.Tensor:
        indices = torch.tensor(tokens_idx_list)
        tokens_mask = self._get_default_mask()
        tokens_mask[indices] = 1
        return tokens_mask

    def _get_tokens_list(self, token_mask) -> Iterable[str]:
        return [self._vocab[idx.item()] for idx in torch.where(token_mask == True)[0]]
