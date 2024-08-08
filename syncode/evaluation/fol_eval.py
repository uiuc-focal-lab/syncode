"""
Adapted from https://github.com/teacherpeterpan/Logic-LLM. Use Prover9 to solve first-order logic problems.
"""
import random
import re
from typing import Optional
from mxeval.data import write_jsonl
from tqdm import tqdm
import signal
from syncode.parsers import create_base_parser
from syncode.parsers.grammars.grammar import Grammar

prompt_template = """Given a problem description and a question. The task is to parse the problem and the question into first-order logic formulars.
The grammar of the first-order logic formular is defined as follows:
1) logical conjunction of expr1 and expr2: expr1 ∧ expr2
2) logical disjunction of expr1 and expr2: expr1 ∨ expr2
3) logical exclusive disjunction of expr1 and expr2: expr1 ⊕ expr2
4) logical negation of expr1: ¬expr1
5) expr1 implies expr2: expr1 → expr2
6) expr1 if and only if expr2: expr1 ↔ expr2
7) logical universal quantification: ∀x
8) logical existential quantification: ∃x
------
Problem:
All people who regularly drink coffee are dependent on caffeine. People either regularly drink coffee or joke about being addicted to caffeine. No one who jokes about being addicted to caffeine is unaware that caffeine is a drug. Rina is either a student and unaware that caffeine is a drug, or neither a student nor unaware that caffeine is a drug. If Rina is not a person dependent on caffeine and a student, then Rina is either a person dependent on caffeine and a student, or neither a person dependent on caffeine nor a student.
Question:
Based on the above information, is the following statement true, false, or uncertain? Rina is either a person who jokes about being addicted to caffeine or is unaware that caffeine is a drug.
Based on the above information, is the following statement true, false, or uncertain? If Rina is either a person who jokes about being addicted to caffeine and a person who is unaware that caffeine is a drug, or neither a person who jokes about being addicted to caffeine nor a person who is unaware that caffeine is a drug, then Rina jokes about being addicted to caffeine and regularly drinks coffee.
###
Predicates:
Dependent(x) ::: x is a person dependent on caffeine.
Drinks(x) ::: x regularly drinks coffee.
Jokes(x) ::: x jokes about being addicted to caffeine.
Unaware(x) ::: x is unaware that caffeine is a drug.
Student(x) ::: x is a student.
Premises:
∀x (Drinks(x) → Dependent(x)) ::: All people who regularly drink coffee are dependent on caffeine.
∀x (Drinks(x) ⊕ Jokes(x)) ::: People either regularly drink coffee or joke about being addicted to caffeine.
∀x (Jokes(x) → ¬Unaware(x)) ::: No one who jokes about being addicted to caffeine is unaware that caffeine is a drug. 
(Student(rina) ∧ Unaware(rina)) ⊕ ¬(Student(rina) ∨ Unaware(rina)) ::: Rina is either a student and unaware that caffeine is a drug, or neither a student nor unaware that caffeine is a drug. 
¬(Dependent(rina) ∧ Student(rina)) → (Dependent(rina) ∧ Student(rina)) ⊕ ¬(Dependent(rina) ∨ Student(rina)) ::: If Rina is not a person dependent on caffeine and a student, then Rina is either a person dependent on caffeine and a student, or neither a person dependent on caffeine nor a student.
Conclusion:
Jokes(rina) ⊕ Unaware(rina) ::: Rina is either a person who jokes about being addicted to caffeine or is unaware that caffeine is a drug.
((Jokes(rina) ∧ Unaware(rina)) ⊕ ¬(Jokes(rina) ∨ Unaware(rina))) → (Jokes(rina) ∧ Drinks(rina)) ::: If Rina is either a person who jokes about being addicted to caffeine and a person who is unaware that caffeine is a drug, or neither a person who jokes about being addicted to caffeine nor a person who is unaware that caffeine is a drug, then Rina jokes about being addicted to caffeine and regularly drinks coffee.
------
Problem:
Miroslav Venhoda was a Czech choral conductor who specialized in the performance of Renaissance and Baroque music. Any choral conductor is a musician. Some musicians love music. Miroslav Venhoda published a book in 1946 called Method of Studying Gregorian Chant.
Question:
Based on the above information, is the following statement true, false, or uncertain? Miroslav Venhoda loved music.
Based on the above information, is the following statement true, false, or uncertain? A Czech person wrote a book in 1946.
Based on the above information, is the following statement true, false, or uncertain? No choral conductor specialized in the performance of Renaissance.
###
Predicates:
Czech(x) ::: x is a Czech person.
ChoralConductor(x) ::: x is a choral conductor.
Musician(x) ::: x is a musician.
Love(x, y) ::: x loves y.
Author(x, y) ::: x is the author of y.
Book(x) ::: x is a book.
Publish(x, y) ::: x is published in year y.
Specialize(x, y) ::: x specializes in y.
Premises:
Czech(miroslav) ∧ ChoralConductor(miroslav) ∧ Specialize(miroslav, renaissance) ∧ Specialize(miroslav, baroque) ::: Miroslav Venhoda was a Czech choral conductor who specialized in the performance of Renaissance and Baroque music.
∀x (ChoralConductor(x) → Musician(x)) ::: Any choral conductor is a musician.
∃x (Musician(x) ∧ Love(x, music)) ::: Some musicians love music.
Book(methodOfStudyingGregorianChant) ∧ Author(miroslav, methodOfStudyingGregorianChant) ∧ Publish(methodOfStudyingGregorianChant, year1946) ::: Miroslav Venhoda published a book in 1946 called Method of Studying Gregorian Chant.
Conclusion:
Love(miroslav, music) ::: Miroslav Venhoda loved music.
∃y (∃x (Czech(x) ∧ Author(x, y) ∧ Book(y) ∧ Publish(y, year1946))) ::: A Czech person wrote a book in 1946.
¬∃x (ChoralConductor(x) ∧ Specialize(x, renaissance)) ::: No choral conductor specialized in the performance of Renaissance.
------
Problem:
[[PROBLEM]]
Question:
[[QUESTION]]
###
"""

class FOLEval:
    @staticmethod
    def run_eval(syncode, out_path: Optional[str]=None, debug_task_id=None):
        problems = syncode.dataset.problems[:100]
        if debug_task_id is not None:
            problems = [problems[debug_task_id]]
        
        if syncode.grammar_decoder is not None:
            syncode.grammar_decoder.parse_output_only = True # Do not parse input+output

        pbar = tqdm(total=len(problems) * syncode.num_samples)
        results = {}
        samples = []
        count_pass = 0
        count_compile_error = 0
        count_syn_error = 0
        count_exec_error = 0
        fol_parser = create_base_parser(Grammar('prover9'))
        
        for task_id, problem in enumerate(problems):
            results[task_id] = []
            full_prompt = FOLEval._prompt_folio(problem)
            completion = syncode.model.generate_batch_completion_grammar(
                full_prompt, 
                syncode.num_samples,
                stop_words=['\n\n', '------']
                )[0]
            logic_program = completion.split('------')[0]
            
            # Execute the logic program
            answer = None
            compiles = False
            rand_ans = False
            error_message = None

            try:
                fol_parser.parse(logic_program)
                is_parsed = True
            except:
                is_parsed = False

            try:
                program = FOL_Prover9_Program(logic_program)
                if program.compiles:
                    compiles = True
                else:
                    raise Exception("Failed to compile logic program")
                answer, error_message = program.execute_program()
                answer = program.answer_mapping(answer)
            except Exception as e:
                count_exec_error += 1
                print(e)
                error_message = str(e)

            if answer is None:
                answer = random.choice(['A', 'B', 'C'])
                rand_ans = True

            map_label_to_answer = {'True': 'A', 'False': 'B', 'Uncertain': 'C'}
            ground_truth = map_label_to_answer[problem['label']]

            res = dict(
                task_id=task_id,
                passed=(answer == ground_truth),
                compiles=compiles,
                is_parsed=is_parsed,
                random=(rand_ans),
                logic_program=logic_program,
                answer=answer,  
                ground_truth=ground_truth,
                error_message=error_message,
            )
            count_pass += (answer == ground_truth)
            count_compile_error += (not compiles)
            count_syn_error += (not is_parsed)
            samples += [res]
            pbar.update(syncode.num_samples)
        
        if out_path is not None: write_jsonl(out_path, samples)
        
        print(f"Pass rate: {count_pass}/{len(problems)}")
        print(f"Compilation error rate: {count_compile_error}/{len(problems)}")
        print(f"Execution error rate: {count_exec_error}/{len(problems)}")
        print(f"Syntax error rate: {count_syn_error}/{len(problems)}")
        pbar.close()

    @staticmethod
    def _prompt_folio(test_data):
        problem = test_data['context']
        question = test_data['question'].strip()
        full_prompt = prompt_template.replace('[[PROBLEM]]', problem).replace('[[QUESTION]]', question)
        return full_prompt

class FOL_Parser:
    def __init__(self) -> None:
        self.op_ls = ['⊕', '∨', '∧', '→', '↔', '∀', '∃', '¬', '(', ')', ',']

        self.sym_reg = re.compile(r'[^⊕∨∧→↔∀∃¬(),]+')

        # modified a bit. 
        self.cfg_template = """
        S -> F | Q F | '¬' S | '(' S ')'
        Q -> QUANT VAR | QUANT VAR Q
        F -> '¬' '(' F ')' | '(' F ')' | F OP F | L
        OP -> '⊕' | '∨' | '∧' | '→' | '↔'
        L -> '¬' PRED '(' TERMS ')' | PRED '(' TERMS ')'
        TERMS -> TERM | TERM ',' TERMS
        TERM -> CONST | VAR
        QUANT -> '∀' | '∃'
        """

    def parse_text_FOL_to_tree(self, rule_str):
        """
            Parse a text FOL rule into nltk.tree
            
            Returns: nltk.tree, or None if the parse fails
        """
        ## NOTE: currenly we don't support FOL string that does not follow the grammar defined above. 
        # rule_str = self.reorder_quantifiers(rule_str)
        import nltk
        r, parsed_fol_str = self.msplit(rule_str)
        cfg_str = self.make_cfg_str(r)
        
        grammar = nltk.CFG.fromstring(cfg_str)
        parser = nltk.ChartParser(grammar)
        # note this function might run forever if the string is not parsable
        tree = parser.parse_one(r) 
        
        return tree
    
    def reorder_quantifiers(self, rule_str):
        matches = re.findall(r'[∃∀]\w', rule_str)
        for match in matches[::-1]:
            rule_str = '%s ' % match + rule_str.replace(match, '', 1)
        return rule_str

    def msplit(self, s):
        for op in self.op_ls:
            s = s.replace(op, ' %s ' % op)
        r = [e.strip() for e in s.split()]
        #remove ' from the string if it contains any: this causes error in nltk cfg parsing
        r = [e.replace('\'', '') for e in r]
        r = [e for e in r if e != '']
        
        # deal with symbols with spaces like "dc universe" and turn it to "DcUniverse"
        res = []
        cur_str_ls = []
        for e in r:
            if (len(e) > 1) and self.sym_reg.match(e):            
                cur_str_ls.append(e[0].upper() + e[1:])            
            else:
                if len(cur_str_ls) > 0:
                    res.extend([''.join(cur_str_ls), e])
                else:
                    res.extend([e])
                cur_str_ls = []
        if len(cur_str_ls) > 0:
            res.append(''.join(cur_str_ls))
        
        # re-generate the FOL string
        make_str_ls = []
        for ind, e in enumerate(r):
            if re.match(r'[⊕∨∧→↔]', e):
                make_str_ls.append(' %s ' % e)
            elif re.match(r',', e):
                make_str_ls.append('%s ' % e)
            # a logical variable
            elif (len(e) == 1) and re.match(r'\w', e):
                if ((ind - 1) >= 0) and ((r[ind-1] == '∃') or (r[ind-1] == '∀')):
                    make_str_ls.append('%s ' % e)
                else:
                    make_str_ls.append(e)
            else:
                make_str_ls.append(e)
        
        return res, ''.join(make_str_ls)


    def make_cfg_str(self, token_ls):
        """
        NOTE: since nltk does not support reg strs like \w+, we cannot separately recognize VAR, PRED, and CONST.
        Instead, we first allow VAR, PRED, and CONST to be matched with all symbols found in the FOL; once the tree is
        parsed, we then go back and figure out the exact type of each symbols
        """
        sym_ls = list(set([e for e in token_ls if self.sym_reg.match(e)]))
        sym_str = ' | '.join(["'%s'" % s for s in sym_ls])
        cfg_str = self.cfg_template + 'VAR -> %s\nPRED -> %s\nCONST -> %s' % (sym_str,sym_str,sym_str)
        return cfg_str

    def find_variables(self, lvars, tree):
        if isinstance(tree, str):
            return
        
        if tree.label() == 'VAR':
            lvars.add(tree[0])
            return
        
        for child in tree:
            self.find_variables(lvars, child)

    def symbol_resolution(self, tree):
        lvars, consts, preds = set(), set(), set()
        self.find_variables(lvars, tree)
        self.preorder_resolution(tree, lvars, consts, preds)
        return lvars, consts, preds


    def preorder_resolution(self, tree, lvars, consts, preds):
        # reached terminal nodes
        if isinstance(tree, str):
            return
        
        if tree.label() == 'PRED':
            preds.add(tree[0])
            return
        
        if tree.label() == 'TERM':
            sym = tree[0][0]
            if sym in lvars:
                tree[0].set_label('VAR')
            else:
                tree[0].set_label('CONST')
                consts.add(sym)
            return
        
        for child in tree:
            self.preorder_resolution(child, lvars, consts, preds)

class FOL_Formula:
    def __init__(self, str_fol) -> None:
        def parse_with_timeout(str_fol, timeout):
            def raise_timeout_error(signum, frame):
                raise TimeoutError("Parse timed out!")
            
            # Set the signal handler and a timeout alarm
            signal.signal(signal.SIGALRM, raise_timeout_error)
            signal.alarm(timeout)
            
            try:
                tree = self.parser.parse_text_FOL_to_tree(str_fol)
            finally:
                # Disable the alarm
                signal.alarm(0)
            
            return tree

        try:
            self.parser = FOL_Parser()
            tree = parse_with_timeout(str_fol, 10)
            self.tree = tree
            self.is_valid = tree is not None
            if self.is_valid:
                self.variables, self.constants, self.predicates = self.parser.symbol_resolution(tree)
        except TimeoutError as e:
            print("Parsing timed out")
            # Handle timeout
            tree = None
            self.is_valid = False 
    
    def __str__(self) -> str:
        _, rule_str = self.parser.msplit(''.join(self.tree.leaves()))
        return rule_str
    
    def is_valid(self):
        return self.is_valid

    def _get_formula_template(self, tree, name_mapping):
        for i, subtree in enumerate(tree):
            if isinstance(subtree, str):
                # Modify the leaf node label
                if subtree in name_mapping:
                    new_label = name_mapping[subtree]
                    tree[i] = new_label
            else:
                # Recursive call to process this subtree
                self._get_formula_template(subtree, name_mapping)

    def get_formula_template(self):
        template = self.tree.copy(deep=True)
        name_mapping = {}
        for i, f in enumerate(self.predicates):
            name_mapping[f] = 'F%d' % i
        for i, f in enumerate(self.constants):
            name_mapping[f] = 'C%d' % i

        self._get_formula_template(template, name_mapping)
        self.template = template
        _, self.template_str = self.parser.msplit(''.join(self.template.leaves()))
        return name_mapping, self.template_str


class Prover9_FOL_Formula:
    def __init__(self, fol_formula : FOL_Formula) -> None:
        from ply import lex, yacc
        self.tokens = ['QUANT', 'VAR', 'NOT', 'LPAREN', 'RPAREN', 'OP', 'PRED', 'COMMA', 'CONST']

        self.t_QUANT = r'∀|∃'
        self.t_NOT = r'¬'
        self.t_LPAREN = r'\('
        self.t_RPAREN = r'\)'
        self.t_OP = r'⊕|∨|∧|→|↔'
        self.t_COMMA = r','

        if len(fol_formula.variables) > 0:
            self.t_VAR = r'|'.join(list(fol_formula.variables))
        else:
            self.t_VAR = r'x'
        
        if len(fol_formula.predicates) > 0:
            self.t_PRED = r'|'.join(list(fol_formula.predicates))
        else:
            self.t_PRED = r'PRED'

        if len(fol_formula.constants) > 0:
            self.t_CONST = r'|'.join(list(fol_formula.constants))
        else:
            self.t_CONST = r'0'

        self.precedence = (
            ('left', 'OP'),
            ('right', 'NOT'),
        )

        self.t_ignore = ' \t'
        self.lexer = lex.lex(module=self)
        self.parser = yacc.yacc(module=self, write_tables=False, debug=False)
        
        self.formula = self.parse(str(fol_formula))

    def t_error(self, t):
        # print(f"Illegal character {t.value[0]}")
        t.lexer.skip(1)

    # S -> F
    def p_S_F(self, p):
        '''expr : F'''
        p[0] = p[1]

    # S -> QUANT VAR S
    def p_S_quantified_S(self, p):
        '''expr : QUANT VAR expr'''
        if p[1] == "∀":
            p[0] = f"all {p[2]}.({p[3]})"
        elif p[1] == "∃":
            p[0] = f"some {p[2]}.({p[3]})"
    
    # S -> '¬' S
    def p_S_not(self, p):
        '''expr : NOT expr'''
        p[0] = f"not ({p[2]})"

    # F -> '¬' '(' F ')'
    def p_F_not(self, p):
        '''F : NOT LPAREN F RPAREN'''
        p[0] = f"not ({p[3]})"

    # F -> '(' F ')'
    def p_F_paren(self, p):
        '''F : LPAREN F RPAREN'''
        p[0] = p[2]

    # F -> Var
    def p_F_var(self, p):
        '''F : VAR'''
        p[0] = p[1]

    # F -> F OP F
    def p_F_op(self, p):
        '''F : F OP F'''
        if p[2] == "⊕":
            p[0] = f"(({p[1]}) & not ({p[3]})) | (not ({p[1]}) & ({p[3]}))"
        elif p[2] == "∨":
            p[0] = f"({p[1]}) | ({p[3]})"
        elif p[2] == "∧":
            p[0] = f"({p[1]}) & ({p[3]})"
        elif p[2] == "→":
            p[0] = f"({p[1]}) -> ({p[3]})"
        elif p[2] == "↔":
            p[0] = f"({p[1]}) <-> ({p[3]})"

    # F -> L
    def p_F_L(self, p):
        '''F : L'''
        p[0] = p[1]

    # L -> '¬' PRED '(' TERMS ')'
    def p_L_not(self, p):
        '''L : NOT PRED LPAREN TERMS RPAREN'''
        p[0] = f"not {p[2]}({p[4]})"

    # L -> PRED '(' TERMS ')'
    def p_L_pred(self, p):
        '''L : PRED LPAREN TERMS RPAREN'''
        p[0] = f"{p[1]}({p[3]})"

    # TERMS -> TERM
    def p_TERMS_TERM(self, p):
        '''TERMS : TERM'''
        p[0] = p[1]

    # TERMS -> TERM ',' TERMS
    def p_TERMS_TERM_TERMS(self, p):
        '''TERMS : TERM COMMA TERMS'''
        p[0] = f"{p[1]}, {p[3]}"

    # TERM -> CONST
    def p_TERM_CONST(self, p):
        '''TERM : CONST'''
        p[0] = p[1]

    # TERM -> VAR
    def p_TERM_VAR(self, p):
        '''TERM : VAR'''
        p[0] = p[1]

    def p_error(self, p):
        # print("Syntax error at '%s'" % p.value)
        pass

    def parse(self, s):
        return self.parser.parse(s, lexer=self.lexer)   

class FOL_Prover9_Program:
    def __init__(self, logic_program:str, dataset_name = 'FOLIO') -> None:
        self.logic_program = logic_program
        self.compiles = self.parse_logic_program()
        self.dataset_name = dataset_name

    def parse_logic_program(self):
        try:        
            # Split the string into premises and conclusion
            premises_string = self.logic_program.split("Conclusion:")[0].split("Premises:")[1].strip()
            conclusion_string = self.logic_program.split("Conclusion:")[1].strip()

            # Extract each premise and the conclusion using regex
            premises = premises_string.strip().split('\n')
            conclusion = conclusion_string.strip().split('\n')

            self.logic_premises = [premise.split(':::')[0].strip() for premise in premises]
            self.logic_conclusion = conclusion[0].split(':::')[0].strip()

            # convert to prover9 format
            self.prover9_premises = []
            for premise in self.logic_premises:
                fol_rule = FOL_Formula(premise)
                if fol_rule.is_valid == False:
                    return False
                prover9_rule = Prover9_FOL_Formula(fol_rule)
                self.prover9_premises.append(prover9_rule.formula)

            fol_conclusion = FOL_Formula(self.logic_conclusion)
            if fol_conclusion.is_valid == False:
                return False
            self.prover9_conclusion = Prover9_FOL_Formula(fol_conclusion).formula
            return True
        except Exception as e:
            return False

    def execute_program(self):
        from nltk.inference.prover9 import Prover9Command, Expression
        from nltk.sem.logic import NegatedExpression
        try:
            goal = Expression.fromstring(self.prover9_conclusion)
            assumptions = [Expression.fromstring(a) for a in self.prover9_premises]
            timeout = 1000
            
            prover = Prover9Command(goal, assumptions, timeout=timeout)
            result = prover.prove()
            if result:
                return 'True', ''
            else:
                # If Prover9 fails to prove, we differentiate between False and Unknown
                # by running Prover9 with the negation of the goal
                negated_goal = NegatedExpression(goal)
                # negation_result = prover.prove(negated_goal, assumptions)
                prover = Prover9Command(negated_goal, assumptions, timeout=timeout)
                negation_result = prover.prove()
                if negation_result:
                    return 'False', ''
                else:
                    return 'Unknown', ''
        except Exception as e:
            print(e)
            return None, str(e)
        
    def answer_mapping(self, answer):
        if answer == 'True':
            return 'A'
        elif answer == 'False':
            return 'B'
        elif answer == 'Unknown':
            return 'C'
        else:
            raise Exception("Answer not recognized")
        

if __name__ == "__main__":
    # str_fol = '\u2200x (Dog(x) \u2227 WellTrained(x) \u2227 Gentle(x) \u2192 TherapyAnimal(x))'
    # str_fol = '\u2200x (Athlete(x) \u2227 WinsGold(x, olympics) \u2192 OlympicChampion(x))'
    str_fol = '\u2203x \u2203y (Czech(x) \u2227 Book(y) \u2227 Author(x, y) \u2227 Publish(y, year1946))'
    
    fol_rule = FOL_Formula(str_fol)
    if fol_rule.is_valid:
        print(fol_rule)
        # print(fol_rule.isFOL)
        print(fol_rule.variables)
        print(fol_rule.constants)
        print(fol_rule.predicates)
        name_mapping, template = fol_rule.get_formula_template()
        print(template)
        print(name_mapping)


    # str_fol = '\u2200x (Dog(x) \u2227 WellTrained(x) \u2227 Gentle(x) \u2192 TherapyAnimal(x))'
    str_fol = '\u2200x (Athlete(x) \u2227 WinsGold(x, olympics) \u2192 OlympicChampion(x))'
    # str_fol = '¬∀x ∃x(Movie(x) → HappyEnding(x))'
    
    parser = FOL_Parser()

    tree = parser.parse_text_FOL_to_tree(str_fol)
    print(tree)
    tree.pretty_print()
    
    lvars, consts, preds = parser.symbol_resolution(tree)
    print('lvars: ', lvars)
    print('consts: ', consts)
    print('preds: ', preds)

    ## ¬∀x (Movie(x) → HappyEnding(x))
    ## ∃x (Movie(x) → ¬HappyEnding(x))
    # ground-truth: True
    logic_program = """Premises:
    ¬∀x (Movie(x) → HappyEnding(x)) ::: Not all movie has a happy ending.
    Movie(titanic) ::: Titanic is a movie.
    ¬HappyEnding(titanic) ::: Titanic does not have a happy ending.
    Movie(lionKing) ::: Lion King is a movie.
    HappyEnding(lionKing) ::: Lion King has a happy ending.
    Conclusion:
    ∃x (Movie(x) ∧ ¬HappyEnding(x)) ::: Some movie does not have a happy ending.
    """

    # ground-truth: True
    logic_program = """Premises:
    ∀x (Drinks(x) → Dependent(x)) ::: All people who regularly drink coffee are dependent on caffeine.
    ∀x (Drinks(x) ⊕ Jokes(x)) ::: People either regularly drink coffee or joke about being addicted to caffeine.
    ∀x (Jokes(x) → ¬Unaware(x)) ::: No one who jokes about being addicted to caffeine is unaware that caffeine is a drug. 
    (Student(rina) ∧ Unaware(rina)) ⊕ ¬(Student(rina) ∨ Unaware(rina)) ::: Rina is either a student and unaware that caffeine is a drug, or neither a student nor unaware that caffeine is a drug. 
    ¬(Dependent(rina) ∧ Student(rina)) → (Dependent(rina) ∧ Student(rina)) ⊕ ¬(Dependent(rina) ∨ Student(rina)) ::: If Rina is not a person dependent on caffeine and a student, then Rina is either a person dependent on caffeine and a student, or neither a person dependent on caffeine nor a student.
    Conclusion:
    Jokes(rina) ⊕ Unaware(rina) ::: Rina is either a person who jokes about being addicted to caffeine or is unaware that caffeine is a drug.
    """

    # ground-truth: True
    logic_program = """Premises:
    ∀x (Drinks(x) → Dependent(x)) ::: All people who regularly drink coffee are dependent on caffeine.
    ∀x (Drinks(x) ⊕ Jokes(x)) ::: People either regularly drink coffee or joke about being addicted to caffeine.
    ∀x (Jokes(x) → ¬Unaware(x)) ::: No one who jokes about being addicted to caffeine is unaware that caffeine is a drug. 
    (Student(rina) ∧ Unaware(rina)) ⊕ ¬(Student(rina) ∨ Unaware(rina)) ::: Rina is either a student and unaware that caffeine is a drug, or neither a student nor unaware that caffeine is a drug. 
    ¬(Dependent(rina) ∧ Student(rina)) → (Dependent(rina) ∧ Student(rina)) ⊕ ¬(Dependent(rina) ∨ Student(rina)) ::: If Rina is not a person dependent on caffeine and a student, then Rina is either a person dependent on caffeine and a student, or neither a person dependent on caffeine nor a student.
    Conclusion:
    ((Jokes(rina) ∧ Unaware(rina)) ⊕ ¬(Jokes(rina) ∨ Unaware(rina))) → (Jokes(rina) ∧ Drinks(rina)) ::: If Rina is either a person who jokes about being addicted to caffeine and a person who is unaware that caffeine is a drug, or neither a person who jokes about being addicted to caffeine nor a person who is unaware that caffeine is a drug, then Rina jokes about being addicted to caffeine and regularly drinks coffee.
    """

    # ground-truth: Unknown
    logic_program = """Premises:
    Czech(miroslav) ∧ ChoralConductor(miroslav) ∧ Specialize(miroslav, renaissance) ∧ Specialize(miroslav, baroque) ::: Miroslav Venhoda was a Czech choral conductor who specialized in the performance of Renaissance and Baroque music.
    ∀x (ChoralConductor(x) → Musician(x)) ::: Any choral conductor is a musician.
    ∃x (Musician(x) ∧ Love(x, music)) ::: Some musicians love music.
    Book(methodOfStudyingGregorianChant) ∧ Author(miroslav, methodOfStudyingGregorianChant) ∧ Publish(methodOfStudyingGregorianChant, year1946) ::: Miroslav Venhoda published a book in 1946 called Method of Studying Gregorian Chant.
    Conclusion:
    Love(miroslav, music) ::: Miroslav Venhoda loved music.
    """

    # ground-truth: True
    logic_program = """Premises:
    Czech(miroslav) ∧ ChoralConductor(miroslav) ∧ Specialize(miroslav, renaissance) ∧ Specialize(miroslav, baroque) ::: Miroslav Venhoda was a Czech choral conductor who specialized in the performance of Renaissance and Baroque music.
    ∀x (ChoralConductor(x) → Musician(x)) ::: Any choral conductor is a musician.
    ∃x (Musician(x) ∧ Love(x, music)) ::: Some musicians love music.
    Book(methodOfStudyingGregorianChant) ∧ Author(miroslav, methodOfStudyingGregorianChant) ∧ Publish(methodOfStudyingGregorianChant, year1946) ::: Miroslav Venhoda published a book in 1946 called Method of Studying Gregorian Chant.
    Conclusion:
    ∃y ∃x (Czech(x) ∧ Author(x, y) ∧ Book(y) ∧ Publish(y, year1946)) ::: A Czech person wrote a book in 1946.
    """

    # ground-truth: False
    logic_program = """Premises:
    Czech(miroslav) ∧ ChoralConductor(miroslav) ∧ Specialize(miroslav, renaissance) ∧ Specialize(miroslav, baroque) ::: Miroslav Venhoda was a Czech choral conductor who specialized in the performance of Renaissance and Baroque music.
    ∀x (ChoralConductor(x) → Musician(x)) ::: Any choral conductor is a musician.
    ∃x (Musician(x) ∧ Love(x, music)) ::: Some musicians love music.
    Book(methodOfStudyingGregorianChant) ∧ Author(miroslav, methodOfStudyingGregorianChant) ∧ Publish(methodOfStudyingGregorianChant, year1946) ::: Miroslav Venhoda published a book in 1946 called Method of Studying Gregorian Chant.
    Conclusion:
    ¬∃x (ChoralConductor(x) ∧ Specialize(x, renaissance)) ::: No choral conductor specialized in the performance of Renaissance.
    """

    # ground-truth: Unknown
    # Premises:\nall x.(perform_in_school_talent_shows_often(x) -> (attend_school_events(x) & very_engaged_with_school_events(x))) ::: If people perform in school talent shows often, then they attend and are very engaged with school events.\nall x.(perform_in_school_talent_shows_often(x) ^ (inactive_member(x) & disinterested_member(x))) ::: People either perform in school talent shows often or are inactive and disinterested members of their community.\nall x.(chaperone_high_school_dances(x) -> not student_attend_school(x)) ::: If people chaperone high school dances, then they are not students who attend the school.\nall x.((inactive_member(x) & disinterested_member(x)) -> chaperone_high_school_dances(x)) ::: All people who are inactive and disinterested members of their community chaperone high school dances.\nall x.((young_child(x) | teenager(x)) & wish_to_further_academic_careers(x) & wish_to_further_educational_opportunities(x) -> student_attend_school(x)) ::: All young children and teenagers who wish to further their academic careers and educational opportunities are students who attend the school.\n(attend_school_events(bonnie) & very_engaged_with_school_events(bonnie) & student_attend_school(bonnie)) ^ (not attend_school_events(bonnie) & not very_engaged_with_school_events(bonnie) & not student_attend_school(bonnie)) ::: Bonnie either both attends and is very engaged with school events and is a student who attends the school, or she neither attends and is very engaged with school events nor is a student who attends the school.\nConclusion:\nperform_in_school_talent_shows_often(bonnie) ::: Bonnie performs in school talent shows often."
    logic_program = """Premises:
    ∀x (TalentShows(x) → Engaged(x)) ::: If people perform in school talent shows often, then they attend and are very engaged with school events.
    ∀x (TalentShows(x) ∨ Inactive(x)) ::: People either perform in school talent shows often or are inactive and disinterested members of their community.
    ∀x (Chaperone(x) → ¬Students(x)) ::: If people chaperone high school dances, then they are not students who attend the school.
    ∀x (Inactive(x) → Chaperone(x)) ::: All people who are inactive and disinterested members of their community chaperone high school dances.
    ∀x (AcademicCareer(x) → Students(x)) ::: All young children and teenagers who wish to further their academic careers and educational opportunities are students who attend the school.
    Conclusion:
    TalentShows(bonnie) ::: Bonnie performs in school talent shows often.
    """

    # ground-truth: False
    logic_program = """Premises:
    MusicPiece(symphonyNo9) ::: Symphony No. 9 is a music piece.
    ∀x ∃z (¬Composer(x) ∨ (Write(x,z) ∧ MusicPiece(z))) ::: Composers write music pieces.
    Write(beethoven, symphonyNo9) ::: Beethoven wrote Symphony No. 9.
    Lead(beethoven, viennaMusicSociety) ∧ Orchestra(viennaMusicSociety) ::: Vienna Music Society is an orchestra and Beethoven leads the Vienna Music Society.
    ∀x ∃z (¬Orchestra(x) ∨ (Lead(z,x) ∧ Conductor(z))) ::: Orchestras are led by conductors.
    Conclusion:
    ¬Conductor(beethoven) ::: Beethoven is not a conductor."""

    # ground-truth: True
    logic_program = """Predicates:
    JapaneseCompany(x) ::: x is a Japanese game company.
    Create(x, y) ::: x created the game y.
    Top10(x) ::: x is in the Top 10 list.
    Sell(x, y) ::: x sold more than y copies.
    Premises:
    ∃x (JapaneseCompany(x) ∧ Create(x, legendOfZelda)) ::: A Japanese game company created the game the Legend of Zelda.
    ∀x ∃z (¬Top10(x) ∨ (JapaneseCompany(z) ∧ Create(z,x))) ::: All games in the Top 10 list are made by Japanese game companies.
    ∀x (Sell(x, oneMillion) → Top10(x)) ::: If a game sells more than one million copies, then it will be selected into the Top 10 list.
    Sell(legendOfZelda, oneMillion) ::: The Legend of Zelda sold more than one million copies.
    Conclusion:
    Top10(legendOfZelda) ::: The Legend of Zelda is in the Top 10 list."""

    # logic_program = """Premises:
    # ∀x (Listed(x) → ¬NegativeReviews(x)) ::: If the restaurant is listed in Yelp’s recommendations, then the restaurant does not receive many negative reviews.
    # ∀x (GreaterThanNine(x) → Listed(x)) ::: All restaurants with a rating greater than 9 are listed in Yelp’s recommendations.
    # ∃x (¬TakeOut(x) ∧ NegativeReviews(x)) ::: Some restaurants that do not provide take-out service receive many negative reviews.
    # ∀x (Popular(x) → GreaterThanNine(x)) ::: All restaurants that are popular among local residents have ratings greater than 9.
    # GreaterThanNine(subway) ∨ Popular(subway) ::: Subway has a rating greater than 9 or is popular among local residents.
    # Conclusion:
    # TakeOut(subway) ∧ ¬NegativeReviews(subway) ::: Subway provides take-out service and does not receive many negative reviews."""
    
    prover9_program = FOL_Prover9_Program(logic_program)
    answer, error_message = prover9_program.execute_program()
    print(answer)
    
