use core::iter::Iterator;
use std::vec::Vec;
use std::collections::VecDeque;
use regex_automata::{dfa::{self, dense, Automaton}, util::{primitives::StateID, start}, Anchored};
//use pyo3::prelude::*;


/// We represent a terminal as a str representing the regex matching that
/// terminal. This choice is temporary to facilitate inter-language calling.
/// An accept sequence is then a list of str, each a regex.


/// Track states of DFAs with their name. This is useful when iterating over
/// states of more than one DFA.
struct DFAState {
    /// The regex defining this DFA.
    regex: Box<str>,
    /// The state of this DFA.
    state_id: StateID
}


/// Consume the longest prefix of input that is accepted by the DFA, returning
/// the remainder.
///
/// If we reach a dead state, return (false, None). If we consume the entire
/// input and are in a live state, return (true, ""). If we reach a final state
/// and there is still string left, return (true, remainder).
///
/// # Examples
/// ```
/// let re = r"[a-zA-Z_]\w*";
/// let dfa = dense::DFA::new(re).unwrap();
/// 
/// let result = consume_prefix(&dfa, "this_is_a_python_name");
/// assert_eq!(result, (true, Some(String::new())));
/// 
/// let result = consume_prefix(&dfa, "this_is_a_python_name followed_by_other_stuff");
/// assert_eq!(result, (true, Some(String::from(" followed_by_other_stuff"))));
/// 
/// let result = consume_prefix(&dfa, "this_is't_a_python_name");
/// assert_eq!(result, (true, Some(String::from("'t_a_python_name"))));
/// 
/// let result = consume_prefix(&dfa, "'tai'nt_a_python_name");
/// assert_eq!(result, (false, None));
/// ```
fn consume_prefix(dfa: &dyn Automaton, input: &str) -> (bool, Option<String>) {
    // Only match starting from the beginning of the string.
    let config = start::Config::new().anchored(Anchored::Yes);
    let mut state = dfa.start_state(&config).unwrap();
    let mut remainder = None;

    // Iterate over the string char by char.
    for (i, &b) in input.as_bytes().iter().enumerate() {
	state = dfa.next_state(state, b);

	    if dfa.is_special_state(state) {
		if dfa.is_match_state(state) {
		    // Store the longest remainder seen so far, as long as the
		    // match hasn't failed.
		    remainder = Some(String::from(&input[i..]));
		} else if dfa.is_dead_state(state) {
		    // If this is the first step, then the remainder will still
		    // be None. The match is only considered failed when it
		    // fails right away.
		    return (remainder != None, remainder);
		}
	}

    }
    // Consumed entire string without failing.
    state = dfa.next_eoi_state(state);
    assert!(dfa.is_match_state(state));
    return (true, Some(String::new()));
}


/// Compute whether the string could match a sequence of terminals starting at a certain state in the first DFA.
/// 
/// Given a DFA D(Q, Σ, δ, q0, F ), a string w ∈ Σ∗, a DFA state q ∈ Q and any sequence of terminals Λ = {τf +1, τf +2 . . . τf +d}, dmatch(w, q, Λ) = true, if either of the following conditions hold:
/// 1. δ∗(w, q) ∈ live(Q) or
/// 2. ∃w1 ∈ Σ∗, w2 ∈ Σ+ such that w1.w2 = w, δ∗(w1, q) ∈ F and Λ = {} or
/// 3. ∃w1 ∈ Σ∗, w2 ∈ Σ∗ such that w1.w2 = w, δ∗(w1, q) ∈ F, and dmatch(w2, qτf +10 , {τf +2 . . . τf +d}) = true where qτf +10 is the start state corresponding to the DFA for τf +1.
/// 
fn dmatch(string: &str, starting_state: DFAState, sequence_of_terminals: Vec<String>) -> bool {
    let dfa = dense::Builder::new().configure(dense::DFA::config().start_kind(dfa::StartKind::Anchored)).build(&starting_state.regex).unwrap();

    // Case 1: the DFA, starting at this state, consumes the entire input and is still alive.
    let mut state = starting_state.state_id;
    for &b in string.as_bytes().iter() {
	state = dfa.next_state(state, b);
    }
    if !dfa.is_dead_state(state) {
	return true;
    }

    // Case 2: The DFA consumes a prefix of the string, leaves a non-zero
    // suffix, and there is no sequence of terminals to follow.
    let mut state = starting_state.state_id;
    for (i, &b) in string.as_bytes().iter().enumerate() {
	state = dfa.next_state(state, b);
	if dfa.is_match_state(state) & sequence_of_terminals.is_empty() & (i < string.len()){
	    return true;
	}
    }

    // Case 3: A prefix of the string is successfully consumed by the DFA, and
    // dmatch is true starting at the next member of sequence_of_terminals.
    let mut state = starting_state.state_id;
    for (i, &b) in string.as_bytes().iter().enumerate() {
	state = dfa.next_state(state, b);
	if dfa.is_match_state(state) {
	    let new_dfa = dense::Builder::new().configure(dense::DFA::config().start_kind(dfa::StartKind::Anchored)).build(&sequence_of_terminals[0]).unwrap();
	    let new_starting_state = new_dfa.start_state(&start::Config::new().anchored(Anchored::Yes)).unwrap();
	    let new_regex = sequence_of_terminals[0].clone();
	    return dmatch(&string[i..], DFAState{regex: new_regex.into(), state_id: new_starting_state}, sequence_of_terminals[1..].to_vec());
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
	    res.push(DFAState{regex: terminal.into(), state_id: state});
	}
    }
    res
}


// #[pymodule]
// fn rust_syncode(_py: Python, m: &PyModule) -> PyResult<()> {
//     m.add_function(wrap_pyfunction!(consume_prefix, m)?)?;

//     Ok(())
// }

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_consume_prefix() {
	let re = r"[a-zA-Z_]\w*";
	let dfa = dense::DFA::new(re).unwrap();
	let result = consume_prefix(&dfa, "this_is_a_python_name");
	assert_eq!(result, (true, Some(String::new())));

	let result = consume_prefix(&dfa, "this_is_a_python_name followed_by_other_stuff");
	assert_eq!(result, (true, Some(String::from(" followed_by_other_stuff"))));

	let result = consume_prefix(&dfa, "this_is't_a_python_name");
	assert_eq!(result, (true, Some(String::from("'t_a_python_name"))));

	let result = consume_prefix(&dfa, "'tai'nt_a_python_name");
	assert_eq!(result, (false, None));
    }

    #[test]
    fn test_dmatch() {
	
    }
}
