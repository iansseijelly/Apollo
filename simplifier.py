from pair import *

OP = {'~', '&', '|'}
NUMER = {'0', '1'}

def simplify(expr: str) -> str:
    # first tokenize 
    pass

def parser(expr: str):
    """
    Parse the next complete expression and return as a Pair object. 
    """
    if not expr:
        return nil 
    if expr[0] == '(':
        next_char = expr[1]
        if next_char == '~':
            pass

def parse_tail(expr):
    """
    Parse an expression without the opening parenthesis.
    """
    if expr == ')':
        return nil
    
    


class TokenizedExpr:

    def __init__(self, expr):
        assert isinstance(expr, str), 'Expression must be a string'
        self.tokenized_expr = expr 
        self.idx = 0 
        self.itor = iter(self)
    
    def __iter__(self):
        while self.idx < len(self.tokenized_expr):
            yield self.tokenized_expr[self.idx]
            self.idx += 1 
