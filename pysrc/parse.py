import expr

"""
parser CFG:
AS --> MD | AS + MD | AS - MD
MD --> R | MD * R | MD / R
R  --> (AS) | n | ndm
where d is token and n, m are integers
"""

class Parser:
    # TODO begin and end aren't global
    def __init__(self, tokens):
        self.tokens = tokens
        self.begin = 0
        self.end = len(tokens) - 1
    
    def peek(self):
        if self.begin == self.end:
            return "NUL"
        return self.tokens[self.begin]

    def consume(self):
        if self.begin != self.end:
            self.begin += 1

    def parse(self) -> expr.Expr:
        return self.parse_add_sub()
    
    def parse_add_sub(self) -> expr.Expr:
        e = self.parse_mul_div()

        curr = self.peek()[0]
        if curr == "ADD":
            self.consume()
            e2 = self.parse_add_sub()
            return expr.Add(e2, e)
        if curr == "SUB":
            self.consume()
            e2 = self.parse_add_sub()
            return expr.Sub(e2, e)
        
        return e

    def parse_mul_div(self) -> expr.Expr:
        e = self.parse_base()

        curr = self.peek()[0]
        if curr == "MUL":
            self.consume()
            e2 = self.parse_mul_div()
            return expr.Mul(e2, e)
        if curr == "DIV":
            self.consume()
            e2 = self.parse_mul_div()
            return expr.Div(e2, e)
        
        return e

    def parse_base(self) -> expr.Expr:   
        curr = self.peek()[0]

        if curr == "RPR":
            self.consume()
            p = self.parse_add_sub()
            if self.peek()[0] == "LPR":
                self.consume()
                return p
        
        if curr == "NUM":
            v1 = self.peek()[1]
            self.consume()

            if self.peek() == "DIE":
                self.consume()
                if self.peek() == "NUM":
                    v2 = self.peek()[1]
                    self.consume()
                    return expr.Roll(v1, v2)
            else:
                return expr.Num(v1)

    def eval(self):
        return self.parse().eval()