use core::iter::Iterator;
use pyo3::prelude::*;
use pyo3::pybacked::PyBackedStr;
use regex_automata::{dfa::Automaton, util::primitives::StateID};
//use std::iter::zip;
use std::{collections::HashMap, vec::Vec};
mod dfa;
use dfa::{all_dfa_states, DFABuilder, DFAState};

/// A struct to encapsulate a cache for building DFAs. This has too many layers
/// of indirection; for now it's just proof of concept.
struct Masker {
    dfa_builder: DFABuilder,
}

impl Masker {
    /// Compute whether the string could match a sequence of terminals starting at a certain state in the first DFA.
    ///
    /// Given a DFA D(Q, Σ, δ, q0, F ), a string w ∈ Σ∗, a DFA state q ∈ Q and any sequence of terminals Λ = {τf +1, τf +2 . . . τf +d}, dmatch(w, q, Λ) = true, if either of the following conditions hold:
    /// 1. δ∗(w, q) ∈ live(Q) or
    /// 2. ∃w1 ∈ Σ∗, w2 ∈ Σ+ such that w1.w2 = w, δ∗(w1, q) ∈ F and Λ = {} or
    /// 3. ∃w1 ∈ Σ∗, w2 ∈ Σ∗ such that w1.w2 = w, δ∗(w1, q) ∈ F, and dmatch(w2, qτf +10 , {τf +2 . . . τf +d}) = true where qτf +10 is the start state corresponding to the DFA for τf +1.
    ///
    fn dmatch(
        &mut self,
        string: &str,
        starting_state: &mut DFAState,
        sequence_of_terminals: Vec<&str>,
    ) -> bool {
	println!("{} {}", string, starting_state.regex);

	// We'll need this later.
        let initial_state = starting_state.state_id.clone();
        let mut state: StateID;
        // Case 1: the DFA, starting at this state, consumes the entire input and is still alive.
        state = starting_state.advance(string);
//	println!("{:?}", state);
        // Neither dead nor quit means we could match in the future and so are live.
        if !(starting_state.dfa.is_dead_state(state) || starting_state.dfa.is_quit_state(state)) {
            return true;
        }

        // Case 2: The DFA consumes a prefix of the string, leaves a non-zero
        // suffix, and there is no sequence of terminals to follow. Assume that
        // grammars respect the maximum munch principle, so w1 is the maximal
        // matching prefix.
        starting_state.state_id = initial_state; // Reset to initial state.
	let mut index_reached: usize = 0;
        for (i, c) in string.char_indices() {
            state = starting_state.consume_character(c);
	    if starting_state.dfa.is_dead_state(state) | starting_state.dfa.is_quit_state(state) {
		break;
	    }

	    if starting_state.dfa.is_match_state(state) {
		index_reached = i;
	    }
        }

	if index_reached > 0 && sequence_of_terminals.is_empty() {
	    return true;
	}
	
        // Case 3: A prefix of the string is successfully consumed by the DFA, and
        // dmatch is true starting at the next member of sequence_of_terminals.
        starting_state.state_id = initial_state;
        for (i, c) in string.char_indices() {
            state = starting_state.consume_character(c);

	    if starting_state.dfa.is_match_state(state) || !starting_state.dfa.is_dead_state(state) {
		continue;
	    }

            // Handle case where we consume one character too many by slicing
            // the string before the character we just saw, but only if we
            // ended up matching at least one character.
            if starting_state.dfa.is_dead_state(state) && !sequence_of_terminals.is_empty() && i > 0
            {
                let mut new_dfa = self.dfa_builder.build_dfa(sequence_of_terminals[0]);
                return self.dmatch(
                    &string.chars().collect::<String>()[(i-1)..],
                    &mut new_dfa,
                    sequence_of_terminals[1..].to_vec(),
                );
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
    fn dfa_mask(
        &mut self,
        state: &mut DFAState,
        terminal_sequence: &Vec<&str>,
        vocabulary: &Vec<&str>,
    ) -> Vec<bool> {
        let mut mask: Vec<bool> = Vec::new();
        for token in vocabulary {
	    // Since the state is mutated by dmatch (potentially bad API design
	    // on my part), make a new one each time we try to match a token.
	    let mut starting_state = state.clone();
            mask.push(self.dmatch(token, &mut starting_state, terminal_sequence.clone()));
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
        _length_of_terminal_sequences: usize,
    ) -> HashMap<(DFAState, Vec<&'a str>), Vec<bool>> {
        let all_states = all_dfa_states(&lexical_terminals);
        let mut store: HashMap<(DFAState, Vec<&str>), Vec<bool>> = HashMap::new();
        for mut state in all_states {
            for first_terminal in lexical_terminals.iter() {
                //		for second_terminal in lexical_terminals.iter() {
                store.insert(
                    (
                        state.clone(),
                        vec![
                            first_terminal, // second_terminal
                        ],
                    ),
                    self.dfa_mask(
                        &mut state,
                        &vec![
                            first_terminal, // second_terminal
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
fn dfa_mask_store_py<'py>(lexical_terminals: Vec<PyBackedStr>, model_vocabulary: Vec<PyBackedStr>) {
    let mut matcher = Masker {
        dfa_builder: DFABuilder::new(),
    };
    // Nonsense casts to make the compiler happy.
    let terms: Vec<&str> = lexical_terminals
        .iter()
        .map(|s| s.get(..).unwrap())
        .collect();
    let vocab: Vec<&str> = model_vocabulary
        .iter()
        .map(|s| s.get(..).unwrap())
        .collect();
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
        let mut matcher = Masker {
            dfa_builder: DFABuilder::new(),
        };
        let mut starting_state = matcher.dfa_builder.build_dfa(r"[ab]*cd");
        let accept_sequence: Vec<&str> = Vec::new();
        assert!(matcher.dmatch(candidate_string, &mut starting_state, accept_sequence));
    }

    #[test]
    fn test_dmatch_case2() {
        // False in strict mode, true in overapproximation mode (grammar mask).
        let candidate_string = "abbacdd";
        let mut matcher = Masker {
            dfa_builder: DFABuilder::new(),
        };
        let mut starting_state = matcher.dfa_builder.build_dfa(r"[ab]*");
        let accept_sequence: Vec<&str> = Vec::new();
        let mut matcher = Masker {
            dfa_builder: DFABuilder::new(),
        };
        assert!(matcher.dmatch(candidate_string, &mut starting_state, accept_sequence));
    }

    #[test]
    fn test_dmatch_case3() {
        // Illustrative example from page 12 of the paper.
        let candidate_string = "_prime():";
        let mut matcher = Masker {
            dfa_builder: DFABuilder::new(),
        };
        let mut starting_state = matcher.dfa_builder.build_dfa(r"[a-zA-Z_]*");
        starting_state.advance("is");
        let accept_sequence = vec![r"\(", r"\)"];
        assert!(matcher.dmatch(candidate_string, &mut starting_state, accept_sequence));
    }

    #[test]
    fn test_dmatch_case3a() {
        // Consuming next terminal leaves residual string.
        let candidate_string = "abbacde";
        let mut matcher = Masker {
            dfa_builder: DFABuilder::new(),
        };
        let mut starting_state = matcher.dfa_builder.build_dfa(r"[ab]*");
        starting_state.advance("ab");
        let accept_sequence = vec![r"c"];
        let mut matcher = Masker {
            dfa_builder: DFABuilder::new(),
        };
        assert!(matcher.dmatch(candidate_string, &mut starting_state, accept_sequence));
    }

    #[test]
    fn test_dmatch_supports_unicode_fails() {
        // Make sure dmatch works on tokens that are multiple bytes in UTF-8,
        // even when the match should fail.
        let candidate_string = "³Ġt";
        let accept_sequence = vec![];
        let mut matcher = Masker {
            dfa_builder: DFABuilder::new(),
        };
        let mut starting_state = matcher.dfa_builder.build_dfa(r"[a-zA-Z_]*");
        assert!(!matcher.dmatch(candidate_string, &mut starting_state, accept_sequence));
    }

    #[test]
    fn test_dmatch_supports_unicode_case3() {
        // Make sure dmatch works on tokens that are multiple bytes in UTF-8.
        let candidate_string = "iÃ³";

        let accept_sequence = vec![r"\(", r"\)"];
        let mut matcher = Masker {
            dfa_builder: DFABuilder::new(),
        };
        let mut starting_state = matcher.dfa_builder.build_dfa(r"[a-zA-Z_]*");
        assert!(!matcher.dmatch(candidate_string, &mut starting_state, accept_sequence));
    }

    #[test]
    fn test_dmatch_fails_case2() {
        let candidate_string = "3not an id";
        let accept_sequence = vec![];
        let mut matcher = Masker {
            dfa_builder: DFABuilder::new(),
        };
        let mut starting_state = matcher.dfa_builder.build_dfa(r"[a-zA-Z_]*");
        assert!(!matcher.dmatch(candidate_string, &mut starting_state, accept_sequence));
    }

    #[test]
    fn test_dmatch_accepts_matching_input() {
	let candidate_string = "indeed";
	let accept_sequence = vec![r"\(", r"\)"];
        let mut matcher = Masker {
            dfa_builder: DFABuilder::new(),
        };
        let mut starting_state = matcher.dfa_builder.build_dfa(r"[a-zA-Z_]*");
	assert!(matcher.dmatch(candidate_string, &mut starting_state, accept_sequence));
    }

    #[test]
    fn test_dmatch_fails_case3() {
        let candidate_string = "3not an id";
        let accept_sequence = vec![r"\(", r"\)"];
        let mut matcher = Masker {
            dfa_builder: DFABuilder::new(),
        };
        let mut starting_state = matcher.dfa_builder.build_dfa(r"[a-zA-Z_]*");
        assert!(!matcher.dmatch(candidate_string, &mut starting_state, accept_sequence));
    }

    #[test]
    fn test_dfa_mask_name() {
        // Illustrative example from page 13 of the paper.
        let vocabulary = vec!["_prime():", ":#", "¡", " hi", "indeed", "n0pe"];
        let terminal_sequence = vec![r"\(", r"\)"];
        let mut matcher = Masker {
            dfa_builder: DFABuilder::new(),
        };
        let mut starting_state = matcher.dfa_builder.build_dfa(r"[a-zA-Z_]*");
        starting_state.advance("is");
        assert_eq!(
            matcher.dfa_mask(&mut starting_state, &terminal_sequence, &vocabulary),
            vec![true, false, false, false, true, false],
        );
    }

    #[test]
    fn test_dfa_mask_store() {
        let model_vocabulary = vec!["_prime():", ":#", "'''", " hi", "indeed", "n0pe"];
        let lexical_terminals = vec![r"\(", r"\)", r"[a-zA-Z_]*"];
        let mut matcher = Masker {
            dfa_builder: DFABuilder::new(),
        };
        let store = matcher.dfa_mask_store(lexical_terminals, model_vocabulary, 2);
        let candidate_string = "is";
        let mut starting_state = matcher.dfa_builder.build_dfa(r"[a-zA-Z_]*");
        starting_state.advance(&candidate_string);
        assert_eq!(
            store
                .get(&(
                    starting_state,
                    vec![r"\("// , r"\)"
	    ]
                ))
                .unwrap(),
            &vec![true, false, false, false, true, false],
        );
    }
}
