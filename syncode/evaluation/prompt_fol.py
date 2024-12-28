
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

Instructions:
Each premise, conclusion, or intermediate logical statement must end with a confidence level indicating how well it formalizes the given information.  
The confidence levels are: high, mid, or low.  
- Use high when the line is directly supported by the problem.  
- Use mid for lines that involve minor interpretation or slight ambiguity.  
- Use low for lines where a mistake has been made or the formalization is incorrect.

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
∀x (Drinks(x) → Dependent(x)) ::: All people who regularly drink coffee are dependent on caffeine. ::: Confidence: high
∀x (Drinks(x) ⊕ Jokes(x)) ::: People either regularly drink coffee or joke about being addicted to caffeine. ::: Confidence: high
∀x (Jokes(x) → ¬Unaware(x)) ::: No one who jokes about being addicted to caffeine is unaware that caffeine is a drug. ::: Confidence: high
(Student(rina) ∧ Unaware(rina)) ⊕ ¬(Student(rina) ∨ Unaware(rina)) ::: Rina is either a student and unaware that caffeine is a drug, or neither a student nor unaware that caffeine is a drug. ::: Confidence: high
¬(Dependent(rina) ∧ Student(rina)) → (Dependent(rina) ∧ Student(rina)) ⊕ ¬(Dependent(rina) ∨ Student(rina)) ::: If Rina is not a person dependent on caffeine and a student, then Rina is either a person dependent on caffeine and a student, or neither a person dependent on caffeine nor a student. ::: Confidence: high
Conclusion:
Jokes(rina) ⊕ Unaware(rina) ::: Rina is either a person who jokes about being addicted to caffeine or is unaware that caffeine is a drug. ::: Confidence: high
((Jokes(rina) ∧ Unaware(rina)) ⊕ ¬(Jokes(rina) ∨ Unaware(rina))) → (Jokes(rina) ∧ Drinks(rina)) ::: If Rina is either a person who jokes about being addicted to caffeine and a person who is unaware that caffeine is a drug, or neither a person who jokes about being addicted to caffeine nor a person who is unaware that caffeine is a drug, then Rina jokes about being addicted to caffeine and regularly drinks coffee. ::: Confidence: high
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
Czech(miroslav) ∧ ChoralConductor(miroslav) ∧ Specialize(miroslav, renaissance) ∧ Specialize(miroslav, baroque) ::: Miroslav Venhoda was a Czech choral conductor who specialized in the performance of Renaissance and Baroque music. ::: Confidence: high
∀x (ChoralConductor(x) → Musician(x)) ::: Any choral conductor is a musician. ::: Confidence: high
∃x (Musician(x) ∧ Love(x, music)) ::: Some musicians love music. ::: Confidence: high
Book(methodOfStudyingGregorianChant) ∧ Author(miroslav, methodOfStudyingGregorianChant) ∧ Publish(methodOfStudyingGregorianChant, year1946) ::: Miroslav Venhoda published a book in 1946 called Method of Studying Gregorian Chant. ::: Confidence: high
Conclusion:
Love(miroslav, music) ::: Miroslav Venhoda loved music. ::: Confidence: high
∃y (∃x (Czech(x) ∧ Author(x, y) ∧ Book(y) ∧ Publish(y, year1946))) ::: A Czech person wrote a book in 1946. ::: Confidence: high
¬∃x (ChoralConductor(x) ∧ Specialize(x, renaissance)) ::: No choral conductor specialized in the performance of Renaissance. ::: Confidence: high
------
Problem:
All tea drinkers are calm. Some coffee drinkers are energetic. Any person who is calm and energetic at the same time cannot exist.
Question:
Based on the above information, is the following statement true, false, or uncertain? Alex is a tea drinker, a coffee drinker, and calm.
###
Predicates:
Tea(x) ::: x is a tea drinker.
Coffee(x) ::: x is a coffee drinker.
Calm(x) ::: x is calm.
Energetic(x) ::: x is energetic.
Premises:
∀x (Tea(x) → Calm(x)) ::: All tea drinkers are calm. ::: Confidence: high
∃x (Coffee(x) ∧ Energy(x)) ::: Some coffee drinkers are energetic. ::: Confidence: low
∀x ¬(Calm(x) ∧ Energetic(x)) ::: Any person who is calm and energetic at the same time cannot exist. ::: Confidence: high
Conclusion:
Tea(alex) ∧ Coffee(alex) ∧ Calm(alex) ::: Alex is a tea drinker, a coffee drinker, and calm. ::: Confidence: low
------
Problem:
All dog owners love animals. Some cat owners dislike dogs. Anyone who dislikes dogs does not love animals.
Question:
Based on the above information, is the following statement true, false, or uncertain? Bella is a dog owner and dislikes dogs.
###
Predicates:
DogOwner(x) ::: x is a dog owner.
CatOwner(x) ::: x is a cat owner.
LovesAnimals(x) ::: x loves animals.
DislikesDogs(x) ::: x dislikes dogs.
Premises:
∀x (DogOwner(x) → LovesAnimals(x)) ::: All dog owners love animals. ::: Confidence: high
∃x (CatOwner(x) ∧ DislikesDogs(x)) ::: Some cat owners dislike dogs. ::: Confidence: high
∀x (DislikesDogs(x) → LovesAnimals(x)) ::: Anyone who dislikes dogs does not love animals. ::: Confidence: low
Conclusion:
DogOwner(bella) ∧ DislikesDogs(bella) ::: Bella is a dog owner and dislikes dogs. ::: Confidence: low

------
Problem:
[[PROBLEM]]
Question:
[[QUESTION]]
###
"""
