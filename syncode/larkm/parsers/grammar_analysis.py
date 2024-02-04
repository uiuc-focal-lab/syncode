"Provides for superficial grammar analysis."

from collections import Counter, defaultdict
from typing import List, Dict, Iterator, FrozenSet, Set, Tuple

from ..utils import bfs, fzset, classify
from ..exceptions import GrammarError
from ..grammar import Rule, Terminal, NonTerminal, Symbol
from ..common import ParserConf


class RulePtr:
    __slots__ = ('rule', 'index')
    rule: Rule
    index: int

    def __init__(self, rule: Rule, index: int):
        assert isinstance(rule, Rule)
        assert index <= len(rule.expansion)
        self.rule = rule
        self.index = index

    def __repr__(self):
        before = [x.name for x in self.rule.expansion[:self.index]]
        after = [x.name for x in self.rule.expansion[self.index:]]
        return '<%s : %s * %s>' % (self.rule.origin.name, ' '.join(before), ' '.join(after))

    @property
    def next(self) -> Symbol:
        return self.rule.expansion[self.index]

    def advance(self, sym: Symbol) -> 'RulePtr':
        assert self.next == sym
        return RulePtr(self.rule, self.index+1)

    @property
    def is_satisfied(self) -> bool:
        return self.index == len(self.rule.expansion)

    def __eq__(self, other) -> bool:
        if not isinstance(other, RulePtr):
            return NotImplemented
        return self.rule == other.rule and self.index == other.index

    def __hash__(self) -> int:
        return hash((self.rule, self.index))


State = FrozenSet[RulePtr]

# state generation ensures no duplicate LR0ItemSets
class LR0ItemSet:
    __slots__ = ('kernel', 'closure', 'transitions', 'lookaheads')

    kernel: State
    closure: State
    transitions: Dict[Symbol, 'LR0ItemSet']
    lookaheads: Dict[Symbol, Set[Rule]]

    def __init__(self, kernel, closure):
        self.kernel = fzset(kernel)
        self.closure = fzset(closure)
        self.transitions = {}
        self.lookaheads = defaultdict(set)

    def __repr__(self):
        return '{%s | %s}' % (', '.join([repr(r) for r in self.kernel]), ', '.join([repr(r) for r in self.closure]))


class LR1Item:
    rp: RulePtr
    lookahead: Symbol

    def __init__(self, rp: RulePtr, lookahead: Symbol):
        self.rp = rp
        self.lookahead = lookahead
        assert lookahead is not None
    
    def __repr__(self):
        return '%s . %s' % (repr(self.rp), self.lookahead.name)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, LR1Item):
            return NotImplemented
        return self.rp == other.rp and self.lookahead == other.lookahead
    
    def __hash__(self) -> int:
        return hash((self.rp, self.lookahead))

LR1State = FrozenSet[LR1Item]
class LR1ItemSet:
    __slots__ = ('kernel', 'closure', 'transitions')

    kernel: LR1State
    closure: LR1State
    transitions: Dict[Symbol, 'LR1ItemSet']

    def __init__(self, kernel, closure):
        self.kernel = fzset(kernel)
        self.closure = fzset(closure)
        self.transitions = {}

    def __repr__(self):
        return '{%s | %s}' % (', '.join([repr(r) for r in self.kernel]), ', '.join([repr(r) for r in self.closure]))
    

def update_set(set1, set2):
    if not set2 or set1 > set2:
        return False

    copy = set(set1)
    set1 |= set2
    return set1 != copy

def calculate_sets(rules):
    """Calculate FOLLOW sets.

    Adapted from: http://lara.epfl.ch/w/cc09:algorithm_for_first_and_follow_sets"""
    symbols = {sym for rule in rules for sym in rule.expansion} | {rule.origin for rule in rules}

    # foreach grammar rule X ::= Y(1) ... Y(k)
    # if k=0 or {Y(1),...,Y(k)} subset of NULLABLE then
    #   NULLABLE = NULLABLE union {X}
    # for i = 1 to k
    #   if i=1 or {Y(1),...,Y(i-1)} subset of NULLABLE then
    #     FIRST(X) = FIRST(X) union FIRST(Y(i))
    #   for j = i+1 to k
    #     if i=k or {Y(i+1),...Y(k)} subset of NULLABLE then
    #       FOLLOW(Y(i)) = FOLLOW(Y(i)) union FOLLOW(X)
    #     if i+1=j or {Y(i+1),...,Y(j-1)} subset of NULLABLE then
    #       FOLLOW(Y(i)) = FOLLOW(Y(i)) union FIRST(Y(j))
    # until none of NULLABLE,FIRST,FOLLOW changed in last iteration

    NULLABLE = set()
    FIRST = {}
    FOLLOW = {}
    for sym in symbols:
        FIRST[sym]={sym} if sym.is_term else set()
        FOLLOW[sym]=set()

    # Calculate NULLABLE and FIRST
    changed = True
    while changed:
        changed = False

        for rule in rules:
            if set(rule.expansion) <= NULLABLE:
                if update_set(NULLABLE, {rule.origin}):
                    changed = True

            for i, sym in enumerate(rule.expansion):
                if set(rule.expansion[:i]) <= NULLABLE:
                    if update_set(FIRST[rule.origin], FIRST[sym]):
                        changed = True
                else:
                    break

    # Calculate FOLLOW
    changed = True
    while changed:
        changed = False

        for rule in rules:
            for i, sym in enumerate(rule.expansion):
                if i==len(rule.expansion)-1 or set(rule.expansion[i+1:]) <= NULLABLE:
                    if update_set(FOLLOW[sym], FOLLOW[rule.origin]):
                        changed = True

                for j in range(i+1, len(rule.expansion)):
                    if set(rule.expansion[i+1:j]) <= NULLABLE:
                        if update_set(FOLLOW[sym], FIRST[rule.expansion[j]]):
                            changed = True

    return FIRST, FOLLOW, NULLABLE


class GrammarAnalyzer:
    def __init__(self, parser_conf: ParserConf, debug: bool=False, strict: bool=False):
        self.debug = debug
        self.strict = strict

        root_rules = {start: Rule(NonTerminal('$root_' + start), [NonTerminal(start), Terminal('$END')])
                      for start in parser_conf.start}

        rules = parser_conf.rules + list(root_rules.values())
        self.rules_by_origin: Dict[NonTerminal, List[Rule]] = classify(rules, lambda r: r.origin)

        if len(rules) != len(set(rules)):
            duplicates = [item for item, count in Counter(rules).items() if count > 1]
            raise GrammarError("Rules defined twice: %s" % ', '.join(str(i) for i in duplicates))

        for r in rules:
            for sym in r.expansion:
                if not (sym.is_term or sym in self.rules_by_origin):
                    raise GrammarError("Using an undefined rule: %s" % sym)

        self.start_states = {start: self.expand_rule_lr0(root_rule.origin)
                             for start, root_rule in root_rules.items()}

        self.end_states = {start: fzset({RulePtr(root_rule, len(root_rule.expansion))})
                           for start, root_rule in root_rules.items()}

        self.FIRST, self.FOLLOW, self.NULLABLE = calculate_sets(rules)

        if parser_conf.parser_type == 'lr': 
            lr1_root_rules = {start: Rule(NonTerminal('$root_' + start), [NonTerminal(start)])
                    for start in parser_conf.start}
            lr1_rules = parser_conf.rules + list(lr1_root_rules.values())
            assert(len(lr1_rules) == len(set(lr1_rules)))

            self.lr1_rules_by_origin = classify(lr1_rules, lambda r: r.origin)

            # cache RulePtr(r, 0) in r (no duplicate RulePtr objects)
            self.lr1_start_states = {start: 
                                        LR1ItemSet(
                                            [LR1Item(RulePtr(root_rule, 0), NonTerminal('$END'))],  # kernel
                                                self.expand_rule_lr1(
                                                    root_rule.origin, 
                                                    NonTerminal('$END'),
                                                    self.lr1_rules_by_origin)
                                                ) # closure
                                    for start, root_rule in lr1_root_rules.items()}
        else:
            lr0_root_rules = {start: Rule(NonTerminal('$root_' + start), [NonTerminal(start)])
                    for start in parser_conf.start}

            lr0_rules = parser_conf.rules + list(lr0_root_rules.values())
            assert(len(lr0_rules) == len(set(lr0_rules)))

            self.lr0_rules_by_origin = classify(lr0_rules, lambda r: r.origin)

            # cache RulePtr(r, 0) in r (no duplicate RulePtr objects)
            self.lr0_start_states = {start: 
                                     LR0ItemSet(
                                        [RulePtr(root_rule, 0)],  # kernel
                                        self.expand_rule_lr0(root_rule.origin, self.lr0_rules_by_origin) # closure
                                    )
                                    for start, root_rule in lr0_root_rules.items()}
            
    def expand_rule_lr0(
            self, 
            source_rule: NonTerminal, 
            rules_by_origin: Dict[NonTerminal, Iterator[Rule]]=None
            ) -> State:
        "Returns all init_ptrs accessible by rule (recursive)"

        if rules_by_origin is None:
            rules_by_origin = self.rules_by_origin

        init_ptrs = set()
        def _expand_rule(rule: NonTerminal) -> Iterator[NonTerminal]:
            assert not rule.is_term, rule

            for r in rules_by_origin[rule]:
                init_ptr = RulePtr(r, 0)
                init_ptrs.add(init_ptr)

                if r.expansion: # if not empty rule
                    new_r = init_ptr.next
                    if not new_r.is_term: # if non-terminal
                        assert isinstance(new_r, NonTerminal)
                        yield new_r

        for _ in bfs([source_rule], _expand_rule):
            pass

        return fzset(init_ptrs)

    def expand_rule_lr1(
            self, 
            source_rule: NonTerminal, 
            lookahead: Symbol,
            rules_by_origin: Dict[NonTerminal, Iterator[Rule]]=None,
            ) -> LR1State:
        "Returns all lr1states accessible by rule (recursive)"

        if rules_by_origin is None:
            rules_by_origin = self.lr1_rules_by_origin
        
        init_lr1items = set()
        def _expand_rule(rl_tuple: Tuple[NonTerminal, Symbol]) -> Iterator[NonTerminal]:
            rule, lookahead = rl_tuple
            assert not rule.is_term, rule

            for r in rules_by_origin[rule]:
                init_lr1item = LR1Item(RulePtr(r, 0), lookahead)
                init_lr1items.add(init_lr1item)

                if r.expansion:
                    new_r = init_lr1item.rp.next
                    new_lookaheads = []
                    
                    # Compute FIRST of the rest of the expansion
                    populate_lookaheads(r, init_lr1item, new_lookaheads)
                    if len(new_lookaheads) == 0:
                        new_lookaheads.append(lookahead)

                    if not new_r.is_term:
                        assert isinstance(new_r, NonTerminal)
                        for new_lookahead in new_lookaheads:
                            assert new_lookahead is not None
                            yield (new_r, new_lookahead)

        def populate_lookaheads(init_rule, init_lr1item, new_lookaheads):
            for i in range(init_lr1item.rp.index+1, len(init_rule.expansion)):
                if init_rule.expansion[i].is_term:
                    new_lookaheads.append(init_rule.expansion[i])
                    break
                else: # if non-terminal
                    new_lookaheads += list(self.FIRST[init_rule.expansion[i]])
                    if len(self.NULLABLE) == 0 or not init_rule.expansion[i] in self.NULLABLE:
                        break
            
        for _ in bfs([(source_rule, lookahead)], _expand_rule):
            pass
        return fzset(init_lr1items)
