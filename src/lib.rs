use core::iter::Iterator;
use itertools::Itertools;
use regex_automata::{
    dfa::{dense, Automaton},
    util::{primitives::StateID, start},
    Anchored,
};
use std::collections::VecDeque;
use std::hash::{Hash, Hasher};
use std::{collections::HashMap, vec::Vec};
//use pyo3::prelude::*;

/// We represent a terminal as a str representing the regex matching that
/// terminal. This choice is temporary to facilitate inter-language calling.
/// An accept sequence is then a list of str, each a regex.

/// A DFA along with its state. Generic to facilitate experiementation with
/// different implementations of DFA.
#[derive(Clone, Debug)]
struct DFAState {
    /// The regex representing this dfa.
    regex: Box<str>,
    /// Pointer to the DFA on the heap.
    dfa: Box<dense::DFA<Vec<u32>>>,
    /// The state of this DFA. Defaults to the starting state of the DFA.
    state_id: StateID,
}

/// A dense implementation of the DFAState abstraction.
impl DFAState {
    /// Encapsulate the kluge necessary to set up the DFA correctly for Syncode's use case.
    fn new(regex: &str) -> DFAState {
        let dfa = dense::DFA::new(regex).unwrap();
        // We always want the DFA to match starting from the beginning of the string.
        let config = start::Config::new().anchored(Anchored::Yes);
        let state_id = dfa.start_state(&config).unwrap();
        DFAState {
            regex: regex.into(),
            dfa: dfa.into(),
            state_id,
        }
    }

    /// Convenience function to set the state how we want it.
    fn advance(&mut self, input: &str) {
        for &b in input.as_bytes().iter() {
            self.state_id = self.dfa.next_state(self.state_id, b);
        }
    }
}

impl PartialEq for DFAState {
    //! Avoid comparing the actual DFAs: the state and regex are enough to establish equality.
    fn eq(&self, other: &Self) -> bool {
        (self.regex == other.regex) & (self.state_id == other.state_id)
    }
}

impl Eq for DFAState {}

impl Hash for DFAState {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.regex.hash(state);
        self.state_id.hash(state);
    }
}

/// Compute whether the string could match a sequence of terminals starting at a certain state in the first DFA.
///
/// Given a DFA D(Q, Σ, δ, q0, F ), a string w ∈ Σ∗, a DFA state q ∈ Q and any sequence of terminals Λ = {τf +1, τf +2 . . . τf +d}, dmatch(w, q, Λ) = true, if either of the following conditions hold:
/// 1. δ∗(w, q) ∈ live(Q) or
/// 2. ∃w1 ∈ Σ∗, w2 ∈ Σ+ such that w1.w2 = w, δ∗(w1, q) ∈ F and Λ = {} or
/// 3. ∃w1 ∈ Σ∗, w2 ∈ Σ∗ such that w1.w2 = w, δ∗(w1, q) ∈ F, and dmatch(w2, qτf +10 , {τf +2 . . . τf +d}) = true where qτf +10 is the start state corresponding to the DFA for τf +1.
///
fn dmatch(string: &str, starting_state: &DFAState, sequence_of_terminals: Vec<&str>) -> bool {
    let dfa = &starting_state.dfa; // Avoid taking ownership: just copy it from the heap to the stack.

    // Case 1: the DFA, starting at this state, consumes the entire input and is still alive.
    let mut state = starting_state.state_id.clone();
    for &b in string.as_bytes().iter() {
        state = dfa.next_state(state, b);
    }

    // Neither dead nor quit means we could match in the future and so are live.
    if !(dfa.is_dead_state(state) | dfa.is_quit_state(state)) {
        return true;
    }

    // Case 2: The DFA consumes a prefix of the string, leaves a non-zero
    // suffix, and there is no sequence of terminals to follow.
    state = starting_state.state_id.clone();
    for (i, &b) in string.as_bytes().iter().enumerate() {
        state = dfa.next_state(state, b);
        if dfa.is_match_state(state) & sequence_of_terminals.is_empty() & (i < string.len()) {
            // Return false here for grammar strict mode.
            return true;
        }
    }

    // Case 3: A prefix of the string is successfully consumed by the DFA, and
    // dmatch is true starting at the next member of sequence_of_terminals.
    state = starting_state.state_id.clone();
    for (i, &b) in string.as_bytes().iter().enumerate() {
        state = dfa.next_state(state, b);
        // Look for the longest possible match --- just because this is a
        // matching state doesn't mean we should recur quite yet.
        if dfa.is_match_state(state) {
            // Consume input so long as we are matching it.
            continue;
        }
        // Compile the dfa for the next terminal, if there are terminals left.
        if !sequence_of_terminals.is_empty() {
            let new_dfa = DFAState::new(&sequence_of_terminals[0]);
            // Call recursively.
            return dmatch(&string[i..], &new_dfa, sequence_of_terminals[1..].to_vec());
        }
    }

    // None of the previous cases succeeded, so dmatch is false.
    false
}

/// Return all states of a dfa by breadth-first search. There exists a private
/// method that returns an iterator over all states. The suggested alternative
/// is to traverse the graph manually. See
/// https://github.com/rust-lang/regex/discussions/1223.
fn states(dfa: &dense::DFA<Vec<u32>>) -> Vec<StateID> {
    let mut queue: VecDeque<StateID> = VecDeque::new();
    let mut explored: Vec<StateID> = Vec::new();

    let start = dfa.start_state(&start::Config::new()).unwrap();

    explored.push(start);
    queue.push_back(start);
    while !queue.is_empty() {
        let v = queue.pop_front().unwrap();
        if dfa.is_dead_state(v) {
            continue;
        }
        for letter in dfa.byte_classes().representatives(0..=255) {
            let next = dfa.next_state(queue.pop_front().unwrap(), letter.as_u8().unwrap());
            if !explored.contains(&next) {
                explored.push(next);
                queue.push_back(next);
            }
        }
    }
    explored
}

/// Compute the union of all states of a list of regexes.
fn all_dfa_states(terminals: &Vec<&str>) -> Vec<DFAState> {
    let mut res = Vec::new();
    for terminal in terminals.into_iter() {
        res.push(DFAState::new(&terminal));
    }
    res
}

/// Compute the mask for a given DFA state, terminal sequence, and vocabulary.
///
/// Mα(q, Λ) = m is a binary mask such that t ∈ set(m) if dmatch(t, q, Λ),
/// where t is a string (token in the LLM's vocabulary), q is a DFA state, and
/// Λ is an accept sequence.
fn dfa_mask(state: &DFAState, terminal_sequence: &Vec<&str>, vocabulary: &Vec<&str>) -> Vec<bool> {
    let mut mask: Vec<bool> = Vec::new();
    for token in vocabulary {
        mask.push(dmatch(token, state, terminal_sequence.clone()));
    }
    mask
}

/// Compute the grammar mask store.
///
/// The mask store is constructed offline by enumerating all DFA states QΩ,
/// considering all possible terminals in Γ, and all tokens in V. The DFA mask
/// store depends on the set of terminals Γ and the model’s vocabulary V. As a
/// result, a unique mask store is created for each grammar and tokenizer
/// combination, and to enhance efficiency, we cache and reuse this table for
/// future inferences.
fn dfa_mask_store<'a>(
    lexical_terminals: Vec<&'a str>,
    model_vocabulary: Vec<&'a str>,
    length_of_terminal_sequences: usize,
) -> HashMap<(DFAState, Vec<&'a str>), Vec<bool>> {
    let all_states = all_dfa_states(&lexical_terminals);
    let mut store: HashMap<(DFAState, Vec<&str>), Vec<bool>> = HashMap::new();
    for state in all_states {
        for first_terminal in lexical_terminals.iter() {
            for second_terminal in lexical_terminals.iter() {
                store.insert(
                    (state.clone(), vec![first_terminal, second_terminal]),
                    dfa_mask(
                        &state,
                        &vec![first_terminal, second_terminal],
                        &model_vocabulary,
                    ),
                );
            }
        }
    }

    store
}

// #[pymodule]
// fn rust_syncode(_py: Python, m: &PyModule) -> PyResult<()> {
//     m.add_function(wrap_pyfunction!(consume_prefix, m)?)?;

//     Ok(())
// }

#[cfg(test)]
mod tests {
    use core::assert_eq;

    use super::*;

    #[test]
    fn test_dmatch_case1() {
        let candidate_string = "abba";
        let starting_state = DFAState::new(r"[ab]*cd");
        let accept_sequence: Vec<&str> = Vec::new();
        assert!(dmatch(candidate_string, &starting_state, accept_sequence));
    }

    #[test]
    fn test_dmatch_case2() {
        // False in strict mode, true in overapproximation mode (grammar mask).
        let candidate_string = "abbacdd";
        let starting_state = DFAState::new(r"[ab]*");
        let accept_sequence: Vec<&str> = Vec::new();
        assert!(dmatch(candidate_string, &starting_state, accept_sequence));
    }

    #[test]
    fn test_dmatch_case3() {
        // Illustrative example from page 12 of the paper.
        let candidate_string = "is_prime():";
        let starting_state = DFAState::new(r"[a-zA-Z_]*");
        let accept_sequence = vec![r"\(", r"\)"];
        assert!(dmatch(candidate_string, &starting_state, accept_sequence));
    }

    #[test]
    fn test_dmatch_fails() {
        let candidate_string = "'not an id";
        let starting_state = DFAState::new(r"[a-zA-Z_]*");
        let accept_sequence = vec![r"\(", r"\)"];
        assert!(!dmatch(candidate_string, &starting_state, accept_sequence));
    }

    #[test]
    fn test_dfa_mask_name() {
        // Illustrative example from page 13 of the paper.
        let mut dfa = DFAState::new(r"[a-zA-Z_]*");
        dfa.advance("is");
        let vocabulary = vec!["_prime():", ":#", "'''", " hi", "indeed", "n0pe"];
        let terminal_sequence = vec![r"\(", r"\)"];
        assert_eq!(
            dfa_mask(&dfa, &terminal_sequence, &vocabulary),
            vec![true, false, false, false, true, false],
        );
    }

    #[test]
    fn test_dfa_mask_store() {
        let model_vocabulary = vec!["_prime():", ":#", "'''", " hi", "indeed", "n0pe"];
	let lexical_terminals = vec![r"\(", r"\)", r"[a-zA-Z_]*"];
	let store = dfa_mask_store(model_vocabulary, lexical_terminals, 2);
	let mut dfa = DFAState::new(r"[a-zA-Z_]*");
	let candidate_string = "is";
	dfa.advance(&candidate_string);
	assert_eq!(
	    store.get(&(dfa, vec![r"\(", r"\)"])).unwrap(),
	    &vec![true, false, false, false, true, false]
	);
    }
}
