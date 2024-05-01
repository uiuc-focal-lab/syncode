## ℹ️ Adding new Grammars

SynCode utilizes Lark Extended Backus–Naur form ([EBNF](https://en.wikipedia.org/wiki/Extended_Backus%E2%80%93Naur_form)) grammars to guide generation, ensuring outputs adhere to specific formats. 
These grammars construct parsers that filter out incompatible tokens during the generation process, resulting in output that follows the grammar's production rules.

Creating grammar for SynCode requires a solid understanding of Lark EBNF grammar. Here's how you can get started:

- Read Lark's grammar documentation [here](https://lark-parser.readthedocs.io/en/latest/grammar.html).
- Review existing grammars for SynCode [here](https://github.com/uiuc-focal-lab/syncode/tree/main/syncode/parsers/grammars).

### LALR(1) or LR(1) Grammars

SynCode supports both LALR(1) and LR(1) parser generators, which require grammars to be unambiguously recognizable by these parser generators. 
An ambiguous grammar may lead to shift-reduce or reduce-reduce conflicts. 
LR(1) is more powerful in terms of representing certain syntax, however common features of most popular formal languages are known to be representable as LALR(1) (and hence also LR(1))

- Currently, similar to Lark, we handle shift-reduce conflicts by prioritizing shift
- In the case of reduce-reduce conflicts, SynCode will halt with an error. Fixing these grammars requires a good understanding of how bottom-up parser generators work.
In most cases, it should be possible to fix these errors by rewriting some of the grammar rules.
However, in some rare cases it is possible that it is impossible to represent the grammar as LR(1)

### Backreferences and Lookarounds

### 1-character Lookahead Lexer Assumption

### Handling indentation and other non-context-free constraints

