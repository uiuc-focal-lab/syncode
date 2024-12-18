use regex_automata::{
    dfa::{dense, Automaton},
    util::{primitives::StateID, start},
    Anchored,
};
use std::collections::{HashMap, VecDeque};
use std::hash::{Hash, Hasher};
use std::rc::Rc;

type DFACache = HashMap<String, Rc<DFA>>;
type DFA = dense::DFA<Vec<u32>>;

/// A DFA along with its state. Generic to facilitate experiementation with
/// different implementations of DFA.
#[derive(Clone, Debug)]
pub struct DFAState {
    /// The regex representing this dfa.
    pub regex: Box<str>,
    /// The actual DFA implementation from the library.
    pub dfa: Rc<DFA>,
    /// The state of this DFA. Defaults to the starting state of the DFA.
    pub state_id: StateID,
}

/// Construct DFAs with caching. Only one of these should be instantiated in
/// the lifetime of the program.
pub struct DFABuilder {
    cache: DFACache,
}

impl DFABuilder {
    /// Initialize with an empty cache.
    pub fn new() -> DFABuilder {
        DFABuilder {
            cache: HashMap::new(),
        }
    }

    /// Return a DFAState, either from the cache or building a new one from scratch.
    // FIXME: Remove the clones from this function to accelerate it further.
    pub fn build_dfa(&mut self, regex: &str) -> DFAState {
        match self.cache.get(regex) {
            Some(dfa) => DFAState::new(regex, dfa.clone()),
            None => {
                let new_dfa = Rc::new(DFA::new(regex).unwrap());
                self.cache.insert(String::from(regex), new_dfa.clone());
                DFAState::new(regex, new_dfa)
            }
        }
    }
}

/// A dense implementation of the DFAState abstraction.
impl DFAState {
    /// Encapsulate the kluge necessary to set up the DFA correctly for Syncode's use case.
    fn new(regex: &str, dfa: Rc<DFA>) -> DFAState {
        // We always want the DFA to match starting from the beginning of the string.
        let config = start::Config::new().anchored(Anchored::Yes);
        let state_id = dfa.start_state(&config).unwrap();
        DFAState {
            regex: regex.into(),
            dfa,
            state_id,
        }
    }

    /// Convenience function to set the state how we want it.
    pub fn advance(&mut self, input: &str) -> StateID {
        for c in input.chars() {
            self.consume_character(c);
        }
        self.state_id
    }

    /// Consume a character, starting at the current state, setting and
    /// returning the new state.
    ///
    /// The logic here is non-trivial, because UTF-8 characters are a variable
    /// number of bytes long, and the underlying DFA has bytes as its input
    /// alphabet.
    pub fn consume_character(&mut self, c: char) -> StateID {
        let char_len = c.len_utf8();
        // Buffer to store character as bytes. UFT-8 characters are at most 4
        // bytes long, so allocate a buffer big enough to store the whole
        // character regardless of how long it turns out to be.
        let mut buf = [0; 4];
        c.encode_utf8(&mut buf);
        for (i, &b) in buf.iter().enumerate() {
            // The number of bytes per character is variable: we only need to
            // feed the number of bytes that the character actually is into the
            // DFA; any more would be incorrect. Break the loop once we've gone
            // past the end of the character.
            if i >= char_len {
                break;
            }
            self.state_id = self.dfa.next_state(self.state_id, b);
        }
        self.state_id
    }

    /// Return all states of a dfa by breadth-first search. There exists a private
    /// method that returns an iterator over all states. The suggested alternative
    /// is to traverse the graph manually. See
    /// https://github.com/rust-lang/regex/discussions/1223.
    pub fn states(&self) -> Vec<StateID> {
        let mut queue: VecDeque<StateID> = VecDeque::new();
        let mut explored: Vec<StateID> = Vec::new();

        let start = self
            .dfa
            .start_state(&start::Config::new().anchored(Anchored::Yes))
            .unwrap();

        explored.push(start);
        queue.push_back(start);
        while !queue.is_empty() {
            let current_state = queue.pop_front().unwrap();
            // Iterate over whole alphabet.
            for letter in self.dfa.byte_classes().representatives(0..=255) {
                let next = self.dfa.next_state(current_state, letter.as_u8().unwrap());
                if !explored.contains(&next) {
                    explored.push(next);
                    queue.push_back(next);
                }
            }
            // Special end-of-input transition.
            let next = self.dfa.next_eoi_state(current_state);
            if !explored.contains(&next) {
                explored.push(next);
                queue.push_back(next);
            }
        }
        explored
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

/// Compute the union of all states of a list of regexes.
pub fn all_dfa_states(terminals: &Vec<&str>) -> Vec<DFAState> {
    let mut res = Vec::new();
    let mut builder = DFABuilder::new();
    for terminal in terminals.iter() {
        let dfa = builder.build_dfa(terminal);
        for state in dfa.states() {
            res.push(DFAState {
                regex: terminal.to_string().into(),
                dfa: dfa.dfa.clone(),
                state_id: state,
            });
        }
    }
    res
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_consume_character_match() {
        let mut dfa_state = DFABuilder::new().build_dfa("a");
        let mut state = dfa_state.consume_character('a');
        state = dfa_state.dfa.next_eoi_state(state);
        assert!(dfa_state.dfa.is_match_state(state));
    }

    #[test]
    fn test_consume_character_fails_to_match() {
        let mut dfa_state = DFABuilder::new().build_dfa("a");
        let mut state = dfa_state.consume_character('b');
        state = dfa_state.dfa.next_eoi_state(state);
        assert!(!dfa_state.dfa.is_match_state(state));
    }

    #[test]
    fn test_advance_match() {
        let mut dfa_state = DFABuilder::new().build_dfa("[ab¥]*");
        let mut state = dfa_state.advance("aabb¥aab");
        state = dfa_state.dfa.next_eoi_state(state);
        assert!(dfa_state.dfa.is_match_state(state));
    }

    #[test]
    fn test_advance_fails_to_match() {
        let mut dfa_state = DFABuilder::new().build_dfa("[ab]*");
        let mut state = dfa_state.advance("aabba¥ab");
        state = dfa_state.dfa.next_eoi_state(state);
        assert!(!dfa_state.dfa.is_match_state(state));
    }

    #[test]
    fn test_advance() {
        let mut dfa_state = DFABuilder::new().build_dfa(r"[a-zA-Z_]*");
        let state = dfa_state.advance("indeed");
        assert!(dfa_state.dfa.is_match_state(state));
    }
}
