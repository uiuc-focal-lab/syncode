use core::iter::Iterator;
use std::iter::zip;
use std::{collections::HashMap, vec::Vec};
use pyo3::prelude::*;
use pyo3::pybacked::PyBackedStr;
use regex_automata::dfa::Automaton;
mod dfa;
use dfa::{DFABuilder, DFAState, all_dfa_states};


/// A struct to encapsulate a cache for building DFAs. This has too many layers
/// of indirection; for now it's just proof of concept.
struct Masker {
    dfa_builder: DFABuilder
}


impl Masker {
    /// Compute whether the string could match a sequence of terminals starting at a certain state in the first DFA.
    ///
    /// Given a DFA D(Q, Σ, δ, q0, F ), a string w ∈ Σ∗, a DFA state q ∈ Q and any sequence of terminals Λ = {τf +1, τf +2 . . . τf +d}, dmatch(w, q, Λ) = true, if either of the following conditions hold:
    /// 1. δ∗(w, q) ∈ live(Q) or
    /// 2. ∃w1 ∈ Σ∗, w2 ∈ Σ+ such that w1.w2 = w, δ∗(w1, q) ∈ F and Λ = {} or
    /// 3. ∃w1 ∈ Σ∗, w2 ∈ Σ∗ such that w1.w2 = w, δ∗(w1, q) ∈ F, and dmatch(w2, qτf +10 , {τf +2 . . . τf +d}) = true where qτf +10 is the start state corresponding to the DFA for τf +1.
    ///
    fn dmatch(&mut self, string: &str, starting_state: &DFAState, sequence_of_terminals: Vec<&str>) -> bool {
	let dfa = &starting_state.dfa; // Avoid taking ownership: just copy it from the heap to the stack.

	// Case 1: the DFA, starting at this state, consumes the entire input and is still alive.
	let mut state = starting_state.state_id;
	for &b in string.as_bytes().iter() {
            state = dfa.next_state(state, b);
	}

	// Neither dead nor quit means we could match in the future and so are live.
	if !(dfa.is_dead_state(state) | dfa.is_quit_state(state)) {
            return true;
	}

	// Case 2: The DFA consumes a prefix of the string, leaves a non-zero
	// suffix, and there is no sequence of terminals to follow.
	state = starting_state.state_id;
	for (i, &b) in string.as_bytes().iter().enumerate() {
            state = dfa.next_state(state, b);
            if dfa.is_match_state(state) & sequence_of_terminals.is_empty() & (i < string.len()) {
		// Return false here for grammar strict mode.
		return true;
            }
	}

	// Case 3: A prefix of the string is successfully consumed by the DFA, and
	// dmatch is true starting at the next member of sequence_of_terminals.
	state = starting_state.state_id;


	let mut buf = [0; 4]; // Buffer to store character as bytes.

	for (i, c) in string.char_indices() {
	    // Iterate over the string one character at a time. Strings are encoded as
	    // UTF-8. A UTF-8 character can be 1 to 4 bytes. regex_automata's DFAs work
	    // with individual bytes, so we have to feed the character 1 byte at a time
	    // into the DFA, regardless of how many bytes the character is actually
	    // encoded as. However, when we recur, we need to slice the string at a
	    // character boundary, so we have to keep track of character boundaries as
	    // well as individual bytes; this way we slice the string at the last
	    // character before the one we failed to accept on. Yes, this is a
	    // hellacious nightmare: I blame R. Pike and K. Thompson directly for
	    // having caused me this pain in this moment.

	    // Break the character down into bytes, storing them in buf.
	    c.encode_utf8(&mut buf);
	    let char_len = c.len_utf8();
	    // Iterate over the bytes in the individual character.
	    for (i, &b) in buf.iter().enumerate() {
		// The number of bytes per character is variable: we only need to
		// feed the number of bytes that the character actually is into the
		// DFA; any more would be incorrect. Break the loop once we've gone
		// past the end of the character. FIXME: does this branch have to
		// be here, or is there a way to avoid branching?
		if i >= char_len {
		    break;
		}
		state = dfa.next_state(state, b);
	    }

            // Look for the longest possible match --- just because this is a
            // matching state doesn't mean we should recur quite yet.
            if dfa.is_match_state(state) {
		// Consume input so long as we are matching it.
		continue;
            }

	    // Handle case where we consume one character too many.
	    if dfa.is_dead_state(state) && i > 0 && !sequence_of_terminals.is_empty() {
		let new_dfa = self.dfa_builder.build_dfa(sequence_of_terminals[0]);
		// Call recursively.
		return self.dmatch(&string[(i-1)..], &new_dfa, sequence_of_terminals[1..].to_vec());
	    }
	}

	// None of the previous cases succeeded, so dmatch is false.
	false
    }

    /// Compute the mask for a given DFA state, terminal sequence, and vocabulary.
    ///
    /// Mα(q, Λ) = m is a binary mask such that t ∈ set(m) if dmatch(t, q, Λ),
    /// where t is a string (token in the LLM's vocabulary), q is a DFA state, and
    /// Λ is an accept sequence.
    fn dfa_mask(&mut self, state: &DFAState, terminal_sequence: &Vec<&str>, vocabulary: &Vec<&str>) -> Vec<bool> 
    {
	let mut mask: Vec<bool> = Vec::new();
	for token in vocabulary {
            mask.push(self.dmatch(token, state, terminal_sequence.clone()));
	}
	mask
    }

    /// Compute the grammar mask store.
    ///
    /// For an integer α, the DFA mask store Mα is a function defined as Mα : QΩ ×
    /// Γα → {0, 1}|V |, where QΩ = ⋃ τ ∈Γ Qτ represents the set of all DFA states
    /// and Γα is a set of α-length terminal sequences. Then Mα(q, Λ) = m is a
    /// binary mask such that t ∈ set(m) if dmatch(t, q, Λ)The mask store is
    /// constructed offline by enumerating all DFA states QΩ considering all
    /// possible terminals in Γ, and all tokens in V. The DFA mask store depends on
    /// the set of terminals Γ and the model’s vocabulary V. As a result, a unique
    /// mask store is created for each grammar and tokenizer combination, and to
    /// enhance efficiency, we cache and reuse this table for future inferences.
    fn dfa_mask_store<'a>(
	&mut self,
	lexical_terminals: Vec<&'a str>,
	model_vocabulary: Vec<&'a str>,
	length_of_terminal_sequences: usize,
    ) -> HashMap<(DFAState, Vec<&'a str>), Vec<bool>>
    {
	let all_states = all_dfa_states(&lexical_terminals);
	let mut store: HashMap<(DFAState, Vec<&str>), Vec<bool>> = HashMap::new();
	for state in all_states {
            for first_terminal in lexical_terminals.iter() {
//		for second_terminal in lexical_terminals.iter() {
                    store.insert(
			(state.clone(), vec![first_terminal, // second_terminal
			]),
			self.dfa_mask(
                            &state,
                            &vec![first_terminal, // second_terminal
			    ],
                            &model_vocabulary,
			),
                    );
//		}
            }
	}

	store
    }

    // /// Implement algorithm 2 from the paper.
    // fn grammar_mask(
    // 	&mut self,
    // 	accept_sequences: Vec<Vec<&str>>,
    // 	remainder: &str,
    // 	model_vocabulary: Vec<&str>,
    // ) -> Vec<bool> {
    // 	let mut res_mask: Vec<bool> = vec![false; model_vocabulary.len()];
    // 	for accept_sequence in accept_sequences {
    //         let dfa = self.dfa_builder.build_dfa(accept_sequence[0]);
    //         dfa.advance(remainder);
    //         let mask = self.dfa_mask(&dfa, &accept_sequence[1..].to_vec(), &model_vocabulary);
    //         for (i, (cur, new)) in zip(res_mask.clone(), mask.clone()).enumerate() {
    // 		res_mask[i] = cur | new;
    //         }
    // 	}
    // 	res_mask
    // }

}


#[pyfunction]
fn dfa_mask_store_py<'py>(
    lexical_terminals: Vec<PyBackedStr>,
    model_vocabulary: Vec<PyBackedStr>,
) {
    let mut matcher = Masker{dfa_builder: DFABuilder::new()};
    // Nonsense casts to make the compiler happy.
    let terms: Vec<&str> = lexical_terminals.iter().map(|s| s.get(..).unwrap()).collect();
    let vocab: Vec<&str> = model_vocabulary.iter().map(|s| s.get(..).unwrap()).collect();
    matcher.dfa_mask_store(terms, vocab, 2);
}

#[pymodule]
fn rust_syncode(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(dfa_mask_store_py, m)?)
}


#[cfg(test)]
mod tests {
    use core::assert_eq;

    use super::*;

    #[test]
    fn test_dmatch_case1() {
        let candidate_string = "abba";
        let starting_state = DFAState::new(r"[ab]*cd");
        let accept_sequence: Vec<&str> = Vec::new();
	let mut matcher = Masker{dfa_builder: DFABuilder::new()};
        assert!(matcher.dmatch(candidate_string, &starting_state, accept_sequence));
    }

    #[test]
    fn test_dmatch_case2() {
        // False in strict mode, true in overapproximation mode (grammar mask).
        let candidate_string = "abbacdd";
        let starting_state = DFAState::new(r"[ab]*");
        let accept_sequence: Vec<&str> = Vec::new();
	let mut matcher = Masker{dfa_builder: DFABuilder::new()};
        assert!(matcher.dmatch(candidate_string, &starting_state, accept_sequence));
    }

    #[test]
    fn test_dmatch_case3a() {
	// Consuming next terminal leaves residual string.
	let candidate_string = "abbacde";
	let mut starting_state = DFAState::new(r"[ab]*");
	starting_state.advance("ab");
	let accept_sequence = vec![r"c"];
	let mut matcher = Masker{dfa_builder: DFABuilder::new()};
	assert!(matcher.dmatch(candidate_string, &starting_state, accept_sequence));
    }

    #[test]
    fn test_dmatch_case3() {
        // Illustrative example from page 12 of the paper.
        let candidate_string = "_prime():";
        let mut starting_state = DFAState::new(r"[a-zA-Z_]*");
	starting_state.advance("is");
        let accept_sequence = vec![r"\(", r"\)"];
	let mut matcher = Masker{dfa_builder: DFABuilder::new()};
        assert!(matcher.dmatch(candidate_string, &starting_state, accept_sequence));
    }

    #[test]
    fn test_dmatch_supports_unicode() {
	// Make sure dmatch works on tokens that are multiple bytes in UTF-8.
        let candidate_string = "¡";
        let starting_state = DFAState::new(r"[a-zA-Z_]*");
        let accept_sequence = vec![r"\(", r"\)"];
	let mut matcher = Masker{dfa_builder: DFABuilder::new()};
        assert!(!matcher.dmatch(candidate_string, &starting_state, accept_sequence));
    }


    #[test]
    fn test_dmatch_fails() {
        let candidate_string = "'not an id";
        let starting_state = DFAState::new(r"[a-zA-Z_]*");
        let accept_sequence = vec![r"\(", r"\)"];
	let mut matcher = Masker{dfa_builder: DFABuilder::new()};
        assert!(!matcher.dmatch(candidate_string, &starting_state, accept_sequence));
    }

    #[test]
    fn test_dfa_mask_name() {
        // Illustrative example from page 13 of the paper.
        let mut dfa = DFAState::new(r"[a-zA-Z_]*");
        dfa.advance("is");
        let vocabulary = vec!["_prime():", ":#", "¡", " hi", "indeed", "n0pe"];
        let terminal_sequence = vec![r"\(", r"\)"];
	let mut matcher = Masker{dfa_builder: DFABuilder::new()};
        assert_eq!(
            matcher.dfa_mask(&dfa, &terminal_sequence, &vocabulary),
            vec![true, false, false, false, true, false],
        );
    }

    #[test]
    fn test_dfa_mask_store() {
        let model_vocabulary = vec!["_prime():", ":#", "'''", " hi", "indeed", "n0pe"];
        let lexical_terminals = vec![r"\(", r"\)", r"[a-zA-Z_]*"];
	let mut matcher = Masker{dfa_builder: DFABuilder::new()};
        let store = matcher.dfa_mask_store(lexical_terminals, model_vocabulary, 2);
        let mut dfa = DFAState::new(r"[a-zA-Z_]*");
        let candidate_string = "is";
        dfa.advance(&candidate_string);
        assert_eq!(
            store.get(&(dfa, vec![r"\("// , r"\)"
	    ])).unwrap(),
            &vec![true, false, false, false, true, false],
        );
    }
}
