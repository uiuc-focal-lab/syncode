from collections import defaultdict
import os, pickle
import time
import torch
import regex
import syncode.common as common
from tqdm import tqdm
from syncode.mask_store.byte_tokenizer import ByteTokenizer
from syncode.mask_store.fsm_set import JointFSMState, FSMSet
from syncode.mask_store.lookup_table import LookupTable
from syncode.parsers import create_base_parser
from syncode.larkm.lexer import TerminalDef
from syncode.parse_result import RemainderState, ParseResult
from syncode.parsers.grammars.grammar import Grammar
from typing import Iterable, Union
from transformers import PreTrainedTokenizer


class MaskStore:
    """
    We build an DFA that consists of DFAs for each terminal. We simulate the DFA by consuming the input string for each terminal DFA.

    There are 3 possible cases for the remainder string:

    1. COMPLETE: In this case, the last token is complete (and cannot be further extended) and we know the type of next terminal. Thus, we need to compute all tokens such that consuming the token leads to a live state for the terminal DFA or it reaches a final state for the terminal DFA.

    2. INCOMPLETE: In this case, the remainder is incomplete and does not match any terminal regex. Thus, we need to compute all tokens such that consuming the token leads to a live state for the current terminal DFA or again it reaches a final state for the current terminal DFA at some point.

    3. MAYBE_COMPLETE: In this case the remainder matches a type of terminal. It may happen that we add to the same matched part of the remainder. In that case, there are two possibilities. i) the matched terminal type does not change and thus we can use the next terminal set computed by assuming that. ii) the matched terminal type changes and then we do not know the next terminal set. Thus, we need to compute all tokens such that consuming the token leads to a live state for the current terminal DFA or again it reaches a final state for the current terminal DFA at some point.
    """
    def __init__(self, 
                 terminals: Iterable[TerminalDef], 
                 tokenizer: PreTrainedTokenizer, 
                 simplifications: dict={}, 
                 special_token_ids: Iterable=[], 
                 indentation: bool=True,
                 mode='grammar_strict', # 'grammar_strict' or 'grammar_mask'
                 ignore_terminals: Iterable[str]=[],
                 parse_table=None
                 ):
        self._vocab = tokenizer.get_vocab()
        self.byte_tokenizer = ByteTokenizer(tokenizer)
        self.special_token_ids = special_token_ids  
        self._mode = mode

        # Create the FSMs for each terminal
        self._fsms = FSMSet(terminals, simplifications)

        # Check if whitespace is in ignore terminals
        self._ignore_whitespace = self.set_ignore_whitespace(terminals, ignore_terminals)
        print(f"Ignore whitespace tokens is {self._ignore_whitespace}", flush=True)
        
        # Iterate through each pair of DFA state and next terminals and store the overapproximate tokens
        self._lookup_table = LookupTable(self._vocab, special_token_ids, indentation=indentation, mode=mode)
        terminal_names = [terminal.name for terminal in terminals]

        followings_terminas_map = None
        if parse_table is not None:
            followings_terminas_map = self._compute_following_terminals_map(terminal_names, parse_table)
        self._store_overapproximate_tokens(terminal_names, self._vocab, followings_terminas_map)

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
    def init_mask_store(
        grammar: Grammar, 
        tokenizer, 
        use_cache=True, 
        logger=None, 
        mode='grammar_strict',
        parse_table=None
    ):
        '''
        Loads the fsm for the given language and tokenizer. If the fsm is not cached, it is created and cached. 
        '''
        tokenizer_name = type(tokenizer).__name__
        fsm_dir = common.SYNCODE_CACHE + 'mask_stores/' + tokenizer_name + '/'
        grammar_hash = grammar.hash()

        # TODO: Hashing using the tokenizer vocab size, this may be problmatic if we have two fine-tuned models with same tokenizer, same vocab size but different vocab
        fsm_path = f'{fsm_dir}{mode}_{grammar_hash}_{tokenizer.vocab_size}.pkl'
        
        if use_cache and os.path.exists(fsm_path):
            try:
                mask_store = pickle.load(open(fsm_path, 'rb'))
                return mask_store
            except: # If we cannot load the file, we will create the fsm from scratch
                pass
    
        print(f"Creating DFA mask store for {tokenizer_name} and {grammar}, may take more than 10 minutes. Caching at {os.path.abspath(fsm_path)}.", flush=True)
        vocab = MaskStore._get_vocab_from_tokenizer(tokenizer)

        base_parser = create_base_parser(grammar)
        simplifications = grammar.simplifications()
        os.makedirs(fsm_dir, exist_ok=True)

        start_time = time.time()
        mask_store = MaskStore(
            base_parser.terminals, 
            tokenizer, 
            simplifications=simplifications, 
            special_token_ids=[tokenizer.eos_token_id], 
            mode=mode, 
            ignore_terminals=base_parser.ignore_tokens, 
            parse_table=parse_table
            )
        print(f"Time taken to create mask store: {time.time() - start_time} seconds", flush=True)

        pickle.dump(mask_store, open(fsm_path, 'wb'))
        return mask_store

    def _get_default_mask(self) -> torch.Tensor:
        mask = torch.zeros(len(self._vocab), dtype=torch.bool)
        return mask

    def _compute_following_terminals_map(self, terminals: Iterable[str], parse_table) -> defaultdict:
        """
        From terminals, filter out terminals that cannot follow the current terminal
        according to the grammar.

        If in the parsing table Action[cur_terminal, parser_state] = 'shift, new_parser_state' then next terminals
        are the terminals that are legal in new_parser_state.
        """
        following_terminals_map = defaultdict(set)
        terminals_set = set(terminals)

        # We iterate through each cur_terminal:    
        for cur_terminal in terminals:
            # We iterate through each parser_state:
            for _, row in parse_table.states.items():
                if cur_terminal in row:
                    action = row[cur_terminal]
                    # -> If we see a shift action to new_parser_state
                    if str(action[0]) == 'Shift':
                        new_parser_state = action[1]
                        for next_terminal in parse_table.states[new_parser_state]:
                            # Lark parse_table stores non-terminals and terminals together
                            if next_terminal in terminals_set:
                                # -> -> we add the terminals that are legal in new_parser_state
                                following_terminals_map[cur_terminal].add(next_terminal)
        
        return following_terminals_map


    def _store_overapproximate_tokens(self, terminals: Iterable[str], vocab: Iterable[str], followings_terminas_map: dict=None):
        """
        Stores the overapproximate tokens for each fsm state and next terminals
        """
        all_fsm_states = self._fsms.states()
        pbar = tqdm(total=len(all_fsm_states))

        for fsm_state in all_fsm_states:
            for token, token_idx in vocab.items():
                is_special_token = token_idx in self.special_token_ids

                if is_special_token:
                    if self._fsms.is_final(fsm_state):
                        self._lookup_table.fsm_state_and_next_terminal_to_tokens_add(
                            fsm_state, '$END', token_idx)
                else:
                    if followings_terminas_map is not None and fsm_state.terminal in followings_terminas_map:
                        following_terminals = followings_terminas_map[fsm_state.terminal]
                    else:
                        following_terminals = terminals

                    self._process_regular_tokens(following_terminals, fsm_state, token_idx, token)
            
            pbar.update(1)

    def _process_regular_tokens(self, terminals, fsm_state, token_idx, token: str):
        # Convert the token to bytes
        # There are two types of tokens: some that convert into a valid utf-8 string. We can just use Python to convert them to bytes. For others, we need to use the byte_tokenizer
        token_bytes = self.byte_tokenizer.decode([token_idx])

        # Replace \t with 4 spaces
        remainder = token_bytes.replace(b'\t', b'    ')

        is_valid, remainder = self._fsms.consume_prefix(fsm_state, remainder)
        if is_valid:
            if len(remainder) == 0:
                # We reached a live state for the current terminal, thus we add the token in all overapproximate sets of next terminals
                for next_terminal in terminals:
                    self._lookup_table.fsm_state_and_next_terminal_to_tokens_add(fsm_state, next_terminal, token_idx)
            else:
                remainder = self.remove_left_whitespace(fsm_state, remainder)

                # We reached the final state while consuming the token, thus we conusme the remainder with all next terminals
                for next_terminal in terminals:
                    initial_state = self._fsms.initial(next_terminal)
                    is_valid, remainder_new = self._fsms.consume_prefix(initial_state, remainder)
                    if self._mode == 'grammar_mask':
                        if is_valid: # In the non-strict mode we overapproximate
                            # We reached a live state for the next terminal, thus we add the 
                            # token in the  overapproximate sets of next terminals
                            self._lookup_table.fsm_state_and_next_terminal_to_tokens_add(fsm_state, next_terminal, token_idx)
                    elif self._mode == 'grammar_strict':
                        if is_valid and len(remainder_new) == 0: 
                            # We reached a live state for the next terminal and the remainder 
                            # is empty, thus we add the token in the exact set of next terminals
                            self._lookup_table.fsm_state_and_next_terminal_to_tokens_add(fsm_state, next_terminal, token_idx)
                    else:
                        raise ValueError(f"Invalid mode: {self._mode}")
                    
        # For COMPLETE case:
        remainder = token_bytes
        remainder = self.remove_left_whitespace(fsm_state, remainder)

        is_valid, remainder = self._fsms.consume_prefix(fsm_state, remainder)
        if is_valid and len(remainder) == 0:
            self._lookup_table.add_exact_lookup(fsm_state, token_idx)


    def remove_left_whitespace(self, fsm_state, remainder: Union[str, bytes]) -> Union[str, bytes]:
        """
        Ignore left space at the start of the terminal. This only helps the efficiency
        e.g. without this say if the model wants to generate ' def' then syncode will force it to generate ' ' and 'def' seperately
        """
        if self._fsms.initial(fsm_state.terminal) == fsm_state and self._ignore_whitespace:
            if isinstance(remainder, bytes) and remainder.startswith(b' '):
                remainder = remainder[1:]
            elif isinstance(remainder, str) and remainder.startswith(' '):
                remainder = remainder[1:]
        return remainder
      

    def _lookup_next_tokens_for_fsm_state(self, fsm_state: JointFSMState, next_terminal) -> torch.Tensor:
        tokens = self._lookup_table.fsm_state_and_next_terminal_to_tokens(fsm_state, next_terminal)
        if tokens == []:
            # TODO: This is a hack. Do something better
            return self._get_default_mask()
        return tokens

    @staticmethod
    def _get_vocab_from_tokenizer(tokenizer, byte_string=False) -> Iterable[str]:
        """
        self.vocab is a list of readable token strings (e.g., ' hello' and '\n')
        sorted by their token IDs (so self.vocab[0] is the first token, etc). 

        if `byte_string` is True, then the vocab is returned as byte strings.
        """
        vocab = [v for k, v in
                        sorted([(t_id, tokenizer.decode([t_id]))
                                for _, t_id in tokenizer.get_vocab().items()])]

        # HACK: Is there a better way to know if a token has a prefix space?
        if 'Llama' in tokenizer.__class__.__name__:
            for i in range(len(vocab)):
                t = vocab[i]
                if 2*len(t) != len(tokenizer.decode([i, i], add_special_tokens=False)):
                    vocab[i] = ' ' + t
                if t == '':
                    vocab[i] = ' '
        
        if byte_string:
            vocab = [t.encode('utf-8') for t in vocab]

        return vocab


    def _lookup_next_tokens(
            self, 
            fsm_states: Iterable[JointFSMState], 
            remainder_state: RemainderState, 
            accept_sequences: Iterable
        ) -> torch.Tensor:
        """
        Lookup the next tokens for the current fsm states and remainder state and accept sequences. 
        """
        overapprox_token_ids = self._get_default_mask()

        # Case when the final string may be incomplete
        for fsm_state in fsm_states:
                for accept_sequence in accept_sequences:
                    if fsm_state.terminal != accept_sequence[0]:
                        continue

                    if remainder_state == RemainderState.COMPLETE:
                            assert len(accept_sequence) == 1 # Since we only store length 1 accept sequences in this case
                            overapprox_token_ids |= self._lookup_table.complete_case_lookup(fsm_state)

                    if remainder_state == RemainderState.INCOMPLETE:
                            overapprox_token_ids |= self._lookup_table.incomplete_case_lookup(fsm_state)
                    
                    if remainder_state == RemainderState.MAYBE_COMPLETE:
                            if len(accept_sequence) == 1:
                                overapprox_token_ids |= self._lookup_table.complete_case_lookup(fsm_state)
                            elif len(accept_sequence) == 2:
                                overapprox_token_ids |= self._lookup_next_tokens_for_fsm_state(fsm_state, accept_sequence[1])
                            elif len(accept_sequence) == 3:
                                # If the DFA state is a final state we can jump to the start of next terminal
                                if self._fsms.is_final(fsm_state): 
                                    ignore_init_state = self._fsms.initial(accept_sequence[1])
                                    overapprox_token_ids |= self._lookup_next_tokens_for_fsm_state(ignore_init_state, accept_sequence[2])
                            else:
                                raise ValueError(f"Invalid accept sequence: {accept_sequence}")
        return overapprox_token_ids

    def get_fsm_states(self, r: ParseResult) -> Iterable[JointFSMState]:
        """
        Returns the DFA state for the current partial code
        """
        cur_incomplete_string = r.remainder
        if cur_incomplete_string is None:
            return []

        cur_fsm_states = self._fsms.compute_fsm_states(cur_incomplete_string)
        return cur_fsm_states

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

        cur_fsm_states = self._fsms.compute_fsm_states(cur_incomplete_string)
        accept_token_mask = self._lookup_next_tokens(
            cur_fsm_states, r.remainder_state, r.accept_sequences)

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
        cur_incomplete_string = r.remainder.encode('utf-8')

        cur_fsm_states = self._fsms.compute_fsm_states(cur_incomplete_string)
        for accept_sequence in r.accept_sequences:
            for fsm_state in cur_fsm_states:
                if fsm_state.terminal == accept_sequence[0]:
                    return True
        return False

    def _list_to_mask(self, tokens_idx_list) -> torch.Tensor:
        indices = torch.tensor(tokens_idx_list)
        tokens_mask = self._get_default_mask()
        tokens_mask[indices] = 1
        return tokens_mask

    def _get_tokens_list(self, token_mask) -> Iterable[str]:
        return [self._vocab[idx.item()] for idx in torch.where(token_mask == True)[0]]
