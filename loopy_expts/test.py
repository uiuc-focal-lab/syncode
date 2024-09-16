from syncode.larkm import Lark, Token, Transformer

grammar_file = open("invariants.lark", "r")
grammar = grammar_file.read()
grammar_file.close()

parser = Lark(grammar, start='start', parser='lalr')
print(parser.parse(
    """
    /*@ 
    loop invariant a; 
    */"""
    ))
