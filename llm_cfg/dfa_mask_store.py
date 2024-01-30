from collections import defaultdict
import time
from typing import Tuple
import interegular
import torch
import regex
from parse_result import IndentationConstraint, RemainderState, ParseResult

class Exception:
    """
    The exception class presents a mapping from the original regex to the simplified regex for certain terminals. 
    There are two reasons for doing this. In some cases, the original regex is complex and requires large DFAs. Computing the overapproximate tokens for such DFAs is expensive. The other reason is that the interegular library does not support some regex features such as lookaheads. Thus, we use the simplified regex to compute the overapproximate tokens.
    """
    def __init__(self, original_regex, simplified_regex):
        self.original_regex = original_regex
        self.simplified_regex = simplified_regex

    def match_original(self, s):
        return regex.match(self.original_regex, s) is not None
    
class DFAMaskStore:
    """
    We build an DFA that consists of DFAs for each terminal. We simulate the DFA by consuming the input string for each terminal DFA.

    There are 3 possible cases for the remainder string:

    1. COMPLETE: In this case, the last token is complete (and cannot be further extended) and we know the type of next terminal. Thus, we need to compute all tokens such that consuming the token leads to a live state for the terminal DFA or it reaches a final state for the terminal DFA.

    2. INCOMPLETE: In this case, the remainder is incomplete and does not match any terminal regex. Thus, we need to compute all tokens such that consuming the token leads to a live state for the current terminal DFA or again it reaches a final state for the current terminal DFA at some point.

    3. MAYBE_COMPLETE: In this case the remainder matches a type of terminal. It may happen that we add to the same matched part of the remainder. In that case, there are two possibilities. i) the matched terminal type does not change and thus we can use the next terminal set computed by assuming that. ii) the matched terminal type changes and then we do not know the next terminal set. Thus, we need to compute all tokens such that consuming the token leads to a live state for the current terminal DFA or again it reaches a final state for the current terminal DFA at some point.
    """
    def __init__(self, terminals: list, vocab, exceptions={}, special_token_ids=[], indentation=True):
        self._terminals_to_dfa = {}
        self._vocab = vocab
        self.anything_else = interegular.fsm.anything_else # This is special character used for the DFAs
        self.exceptions = []      
        self.special_token_ids = special_token_ids  

        for terminal in terminals:
            if terminal.name in exceptions:
                terminal_regex = exceptions[terminal.name]
                self.exceptions.append(Exception(terminal.pattern.to_regexp(), terminal_regex))
            else:
                terminal_regex = terminal.pattern.to_regexp()
            self._terminals_to_dfa[terminal.name] = interegular.parse_pattern(terminal_regex).to_fsm()
        
        # Iterate through each pair of DFA state and next terminals and store the overapproximate tokens
        self._dfa_state_and_next_terminal_to_tokens: defaultdict = defaultdict(list)
        self._incomplete_case_lookup: dict = {}
        self._complete_case_lookup: dict = {}
        self._store_overapproximate_tokens(self._terminals_to_dfa.keys(), vocab)

        self.indentation = indentation
        if indentation:
            self._whitespace_tokens_map: defaultdict = defaultdict(list)
            self._indentation_to_tokens_map: defaultdict = defaultdict(list)
            self._create_indentation_to_tokens_map()
        
        # NOTE: This should be called at the end of the constructor
        self._convert_lookup_from_list_to_mask()  # convert to boolean tensor mask. This is useful for fast union operations

    def _get_default_mask(self) -> torch.Tensor:
        mask = torch.zeros(len(self._vocab), dtype=torch.bool)
        for token_id in self.special_token_ids:
            mask[token_id] = True
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

    def _get_indentation_tokens(self, indent_constraint: IndentationConstraint, get_list=False):
        '''
        Returns the tokens mask for the indentation constraint
        '''
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


    def _store_overapproximate_tokens(self, terminals, vocab):
        for cur_terminal in terminals:
            for dfa_state in self._terminals_to_dfa[cur_terminal].states:
                
                # Initialize the overapproximate tokens for each dfa state
                self._incomplete_case_lookup[(cur_terminal, dfa_state)] = self._get_default_mask()
                self._complete_case_lookup[(cur_terminal, dfa_state)] = []

                for token_idx, token in enumerate(vocab):

                    # For INCOMPLETE case:
                    remainder = token.replace('\t', '    ')
                    is_valid, remainder = self._consume_prefix(self._terminals_to_dfa[cur_terminal], dfa_state, remainder)
                    if is_valid:
                        if remainder is None:
                            # We reached a live state for the current terminal, thus we add the token in all overapproximate sets of next terminals
                            for next_terminal in terminals:
                                self._dfa_state_and_next_terminal_to_tokens[(cur_terminal, dfa_state, next_terminal)].append(token_idx)
                        else:
                            if remainder.startswith(' '): # ignore left space
                                remainder = remainder[1:]

                            # We reached the final state while consuming the token, thus we conusme the remainder with all next terminals
                            for next_terminal in terminals:
                                next_terminal_dfa = self._terminals_to_dfa[next_terminal]
                                is_valid, _ = self._consume_prefix(next_terminal_dfa, next_terminal_dfa.initial, remainder)
                                if is_valid: 
                                    # We reached a live state for the next terminal, thus we add the 
                                    # token in the  overapproximate sets of next terminal
                                    self._dfa_state_and_next_terminal_to_tokens[(cur_terminal, dfa_state, next_terminal)].append(token_idx)

                    # For COMPLETE case:
                    remainder = token
                    if remainder.startswith(' '): # ignore left space
                        remainder = remainder[1:]
                    is_valid, remainder = self._consume_prefix(self._terminals_to_dfa[cur_terminal], dfa_state, remainder)
                    if is_valid:
                        self._complete_case_lookup[(cur_terminal, dfa_state)].append(token_idx)
                
                # Convert the list to boolean tensor mask. This is useful for fast union operations
                self._complete_case_lookup[(cur_terminal, dfa_state)] = self._get_tokens_mask(self._complete_case_lookup[(cur_terminal, dfa_state)])
        

    def _consume_prefix(self, dfa: interegular.FSM, dfa_state, input_str):
        """
        Consume longest prefix of s that is accepted by dfa and return the remainder. 
        If we reach a dead state, return (False, None). 
        If the consumption ends at any live state that is not an accept state, return (True, None).
        If we reach a final state, return (True, remainder).
        """
        state = dfa_state
        longest_accept_index = -1

        if state in dfa.finals:
            longest_accept_index = 0

        for i, symbol in enumerate(input_str):
            if not symbol in dfa.alphabet:
                if not self.anything_else in dfa.alphabet:
                    state = None
                    break
                symbol = self.anything_else

            # Missing transition = transition to dead state
            if not (state in dfa.map and dfa.alphabet[symbol] in dfa.map[state]):
                state = None
                break

            state = dfa.map[state][dfa.alphabet[symbol]]

            if state in dfa.finals:
                longest_accept_index = i+1
        
        if longest_accept_index != -1: # reached accept state at some point
            return (True, input_str[longest_accept_index:])
        elif state != None and dfa.islive(state): # if state is a live state
            return (True, None)
        
        # if we never reach a final state and reach a dead state at some point
        return (False, None)

    def _consume_input(self, dfa, input_str):
        """
        Conumses the input string and returns the final state if it is live, otherwise returns None
        """
        dfa_state = dfa.initial
        # print(repr(input_str))
        for i, symbol in enumerate(input_str):
            # print(i, repr(symbol))
            if not symbol in dfa.alphabet:
                if not self.anything_else in dfa.alphabet:
                    return None
                symbol = self.anything_else
            # Missing transition = transition to dead state
            if not (dfa_state in dfa.map and dfa.alphabet[symbol] in dfa.map[dfa_state]):
                return None
            dfa_state = dfa.map[dfa_state][dfa.alphabet[symbol]]
            
        return dfa_state


    def _DFA_state(self, input_str):
        """
        consume input_str and get the list of pairs of (terminal, dfa_state). This denotes our current DFA state
        """
        DFA_state = []
        for (termianl, dfa) in self._terminals_to_dfa.items():
            dfa_state = self._consume_input(dfa, input_str)
            if dfa_state is not None:
                DFA_state.append((termianl, dfa_state)) 
        return DFA_state
    
    def _convert_lookup_from_list_to_mask(self):
        for key, val in self._dfa_state_and_next_terminal_to_tokens.items():
            self._dfa_state_and_next_terminal_to_tokens[key] = self._get_tokens_mask(val)
            (cur_terminal, dfa_state, _) = key
            self._incomplete_case_lookup[(cur_terminal, dfa_state)] |= self._dfa_state_and_next_terminal_to_tokens[key]
        
        if self.indentation:
            for key, val in self._whitespace_tokens_map.items():
                self._whitespace_tokens_map[key] = self._get_tokens_mask(val)
            for key, val in self._indentation_to_tokens_map.items():
                self._indentation_to_tokens_map[key] = self._get_tokens_mask(val)


    def _lookup_next_tokens_for_dfa_state(self, cur_terminal, dfa_state, next_terminal) -> torch.Tensor:
        tokens = self._dfa_state_and_next_terminal_to_tokens[(cur_terminal, dfa_state, next_terminal)]
        if tokens == []:
            return self._get_default_mask()
        return tokens

    def _lookup_next_tokens(self, DFA_state, r: ParseResult) -> torch.Tensor:
        overapprox_token_ids = self._get_default_mask()
        # print('Time taken for DFA state:', time.time() - start_time, flush=True)

        if r.remainder_state == RemainderState.COMPLETE:
            for (terminal, dfa_state) in DFA_state:
                if terminal in r.next_accept_terminals:
                    overapprox_token_ids |= self._complete_case_lookup[(terminal, dfa_state)]
            return overapprox_token_ids
        
        # Case when the final string may be incomplete
        for (cur_terminal, dfa_state) in DFA_state:
            if r.next_accept_terminals == None: # This is the case when we have incomplete final string
                overapprox_token_ids |= self._incomplete_case_lookup[(cur_terminal, dfa_state)]
            else:
                for next_terminal in r.next_accept_terminals:
                    overapprox_token_ids |= self._lookup_next_tokens_for_dfa_state(cur_terminal, dfa_state, next_terminal)
        return overapprox_token_ids

    def _exception_rule(self, s, exceptions: list[Exception]) -> str:
        for e in exceptions:
            if e.match_original(s):
                return ""
        return s

    def get_overapprox_tokens_mask(self, r: ParseResult, get_list=False):
        # start_time = time.time()
        cur_incomplete_string = self._exception_rule(r.remainder, self.exceptions)
        # print(cur_incomplete_string)
        if cur_incomplete_string is None:
            return torch.ones(len(self._vocab), dtype=torch.bool)

        cur_DFA_state = self._DFA_state(cur_incomplete_string)
        # print(cur_DFA_state)
        
        overapprox_token_ids = self._lookup_next_tokens(cur_DFA_state, r)

        if self.indentation and r.next_ac_indents is not None:
            indent_ac_token = self._get_indentation_tokens(r.next_ac_indents)
            overapprox_token_ids &= indent_ac_token
            # print('Indentation tokens:\n', self._get_tokens_list(indent_ac_token)[:100])
            # print('Overapprox tokens:\n', self._get_tokens_list(overapprox_token_ids)[:100])
        if get_list: # This is useful for testing
            return self._get_tokens_list(overapprox_token_ids)
        # print('Time taken for mask to list:', time.time() - start_time, flush=True)
        return overapprox_token_ids
    
    def _get_tokens_mask(self, tokens_idx_list) -> torch.Tensor:
        indices = torch.tensor(tokens_idx_list)
        tokens_mask = self._get_default_mask()
        tokens_mask[indices] = 1
        return tokens_mask

    def _get_tokens_list(self, token_mask) -> list[str]:
        return [self._vocab[idx.item()] for idx in torch.where(token_mask == True)[0]]
    