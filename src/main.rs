use regex_automata::{
    dfa::{Automaton, dense}, Anchored, util::start
};

fn main() {
    let dfa = dense::DFA::new(r"[a-zA-Z_]\w*").unwrap();
    let result = consume_prefix(&dfa, "this_is_a_python_name");
    assert_eq!(result, (true, Some(String::from(""))));

    let result = consume_prefix(&dfa, "this_is_a_python_name followed_by_other_stuff");
    assert_eq!(result, (true, Some(String::from(" followed_by_other_stuff"))));

    let result = consume_prefix(&dfa, "this_is't_a_python_name");
    assert_eq!(result, (true, Some(String::from("'t_a_python_name"))));

    let result = consume_prefix(&dfa, "'tai'nt_a_python_name");
    assert_eq!(result, (false, None));
}


/// Consume the longest prefix of input that is accepted by the DFA, returning the remainder.
///
/// If we reach a dead state, return (false, None).
/// If we consume the entire input and are in a live state, return (true, "").
/// If we reach a final state and there is still string left, return (true, remainder).
///
/// # Examples
///
/// ```
/// let dfa = dense::DFA::new(r"[a-zA-Z_]\w*")?;
/// let result = consume_prefix(dfa, "this_is_a_python_name");
/// assert_eq!(result, (true, ""));
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
