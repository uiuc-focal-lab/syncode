use core::iter::Iterator;
use std::vec::Vec;
use std::collections::VecDeque;
use regex_automata::{dfa::{self, dense, Automaton}, util::{primitives::StateID, start}, Anchored};
//use pyo3::prelude::*;


/// We represent a terminal as a str representing the regex matching that
/// terminal. This choice is temporary to facilitate inter-language calling.
/// An accept sequence is then a list of str, each a regex.


/// A DFA along with its state.
struct DFAState {
    /// Pointer to the DFA on the heap.
    dfa: Box<dense::DFA<Vec<u32>>>,
    /// The state of this DFA. Defaults to the starting state of the DFA.
    state_id: StateID
}


impl DFAState {
    /// Encapsulate the kluge necessary to set up the DFA correctly for Syncode's use case.
    fn new(
	regex: &str
    ) -> DFAState {
	let dfa = dense::DFA::new(regex).unwrap();
	// We always want the DFA to match starting from the beginning of the string.
	let config = start::Config::new().anchored(Anchored::Yes);
	let state_id = dfa.start_state(&config).unwrap();
	DFAState{dfa: dfa.into(), state_id}
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
    let dfa = starting_state.dfa.clone(); // Avoid taking ownership: just copy it from the heap to the stack.

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
	    continue
	}
	// Compile the dfa for the next terminal, if there are terminals left.
	if !sequence_of_terminals.is_empty() {
	    let new_dfa = DFAState::new(&sequence_of_terminals[0]);
	    // Call recursively.
	    return dmatch(
		&string[i..],
		&new_dfa,
		sequence_of_terminals[1..].to_vec(),
	    );
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
	    let next = dfa.next_state(start, letter.as_u8().unwrap());
	    if !explored.contains(&next) {
		explored.push(next);
	    }
	    queue.push_back(next);
	}
    }
    explored
}


/// Compute the union of all states of a list of regexes.
fn all_dfa_states(terminals: Vec<&str>) -> Vec<DFAState> {
    let mut res: Vec<DFAState> = Vec::new();
    for terminal in terminals {
	let dfa = dense::DFA::new(terminal).unwrap();
	let states = states(&dfa);
	for state in states {
	    res.push(DFAState{dfa: dfa.clone().into(), state_id: state});
	}
    }
    res
}


/// Compute the mask for a given DFA state, terminal sequence, and vocabulary.
///
/// For an integer α, the DFA mask store Mα is a function defined as Mα : QΩ ×
/// Γα → {0, 1}|V |, where QΩ = ⋃ τ ∈Γ Qτ represents the set of all DFA states
/// and Γα is a set of α-length terminal sequences. Then Mα(q, Λ) = m is a
/// binary mask such that t ∈ set(m) if dmatch(t, q, Λ)
fn dfa_mask(state: &DFAState, terminal_sequence: Vec<&str>, vocabulary: Vec<&str>) -> Vec<bool> {
    let mut mask: Vec<bool> = Vec::new();
    for token in vocabulary {
	mask.push(dmatch(token, state, terminal_sequence.clone()));
    }
    mask
}


// #[pymodule]
// fn rust_syncode(_py: Python, m: &PyModule) -> PyResult<()> {
//     m.add_function(wrap_pyfunction!(consume_prefix, m)?)?;

//     Ok(())
// }

#[cfg(test)]
mod tests {
    use core::{assert_eq};

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
	let accept_sequence = [r"\(", r"\)"].to_vec();
	assert!(dmatch(candidate_string, &starting_state, accept_sequence));
    }

    #[test]
    fn test_dmatch_fails() {
	let candidate_string = "'not an id";
	let starting_state = DFAState::new(r"[a-zA-Z_]*");
	let accept_sequence = [r"\(", r"\)"].to_vec();
	assert!(!dmatch(candidate_string, &starting_state, accept_sequence));
    }

    #[test]
    fn test_dfa_mask_name() {
	// Illustrative example from page 13 of the paper.
	let mut dfa = DFAState::new(r"[a-zA-Z_]*");
	dfa.state_id  = dfa.dfa.next_state(dfa.state_id, "i".as_bytes()[0]);
	dfa.state_id  = dfa.dfa.next_state(dfa.state_id, "s".as_bytes()[0]);
	let vocabulary = vec!["_prime():", ":#", "'''", " hi", "_indeed"];
	let terminal_sequence = vec![r"\(", r"\)"];
	assert_eq!(
	    dfa_mask(&dfa, terminal_sequence, vocabulary),
	    vec![true, false, false, false, true],
	);
    }
}
