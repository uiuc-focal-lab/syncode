#!/usr/bin/env python3

import collections

# Trie representation of a vocabulary.
class Trie:
    def __init__(self, value=None):
        self.children = collections.defaultdict(Trie)
        self.value = value

    def insert(self, key, value, depth=0):
        if len(key) == depth:
            self.value = value
        else:
            self.children[key[depth]].insert(key, value, depth + 1)

    @staticmethod
    def from_vocabulary(vocab: list[str]):
        t = Trie()

        for i, token in enumerate(vocab):
            t.insert(token, i)

        return t

    def antimonotonic_filter(self, predicate, key='') -> list[str]:
        this_node_valid = predicate(key)

        if not this_node_valid:
            # Prune using anti-monotonicity: no children will be valid.
            return []

        children_values = []

        for k, c in self.children.items():
            children_values.extend(c.antimonotonic_filter(predicate, key + k))

        # Only return maximal elements.
        if len(children_values) or self.value is None:
            return children_values

        return [self.value]