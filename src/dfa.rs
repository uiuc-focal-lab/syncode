use regex_automata::{
    dfa::{dense, Automaton},
    util::{primitives::StateID, start},
    Anchored,
};
use std::hash::{Hash, Hasher};
use std::collections::{VecDeque, HashMap};

/// We represent a terminal as a str representing the regex matching that
/// terminal. This choice is temporary to facilitate inter-language calling.
/// An accept sequence is then a list of str, each a regex.

/// A DFA along with its state. Generic to facilitate experiementation with
/// different implementations of DFA.
#[derive(Clone, Debug)]
pub struct DFAState {
    /// The regex representing this dfa.
    pub regex: Box<str>,
    /// The actual DFA implementation from the library.
    pub dfa: dense::DFA<Vec<u32>>,
    /// The state of this DFA. Defaults to the starting state of the DFA.
    pub state_id: StateID,
}

type DFACache = HashMap<String, DFAState>;

/// Construct DFAs with caching. Only one of these should be instantiated in
/// the lifetime of the program.
pub struct DFABuilder {
    cache: DFACache
}

impl DFABuilder {
    /// Initialize with an empty cache.
    pub fn new() -> DFABuilder {
	DFABuilder{cache: HashMap::new()}
    }

    /// Return a DFAState, either from the cache or building a new one from scratch.
    pub fn build_dfa(&mut self, regex: &str) -> DFAState {
	if self.cache.contains_key(regex) {
	    return self.cache.get(regex).unwrap().clone();
	} else {
	    let new_dfa = DFAState::new(regex);
	    self.cache.insert(String::from(regex), new_dfa.clone());
	    return new_dfa;
	}
    }
}

/// A dense implementation of the DFAState abstraction.
impl DFAState {
    /// Encapsulate the kluge necessary to set up the DFA correctly for Syncode's use case.
    pub fn new(regex: &str) -> DFAState {
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
    pub fn advance(&mut self, input: &str) {
        for &b in input.as_bytes().iter() {
            self.state_id = self.dfa.next_state(self.state_id, b);
        }
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
