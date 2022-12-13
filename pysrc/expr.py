from random import randint

# parent class for all expressions. should not be used.
class Expr: 
    def eval(self):
        return 0
    
    def __str__(self):
        return ""

# a number
class Num(Expr):
    def __init__(self, val):
        self.val = val
    
    def eval(self):
        return self.val
    
    def __str__(self):
        return str(self.val)

# a die roll expression, representing a pool of dice with the same number of sides
class Roll(Expr):
    # TODO add highest implementation
    def __init__(self, num, die, highest=0):
        self.num = num
        self.die = die
        self.highest = highest
        self.results = []
        self.rolled = False
    
    def eval(self):
        if not self.rolled:
            self.results = [randint(1, self.die) for _ in range(self.num)]
            self.rolled = True
        # self.best = sorted(self.results)[self.highest:]
        return sum(self.results)

    def __str__(self):
        # formatted = map(lambda x : f"**{x}**" if x in self.best else str(x), self.results)
        # return formatted
        # needs to eval once before it can print
        self.eval()
        return f"{sum(self.results)}: {[i for i in self.results]}"

# parent class for all binary operators (add, sub, mul, div). should not be used.
class BinExpr(Expr):
    # Binary expression
    def __init__(self, expr1, expr2):
        self.expr1 = expr1
        self.expr2 = expr2

    def eval(self): 
        # Default eval (never used)
        return [self.expr1.eval(), self.expr2.eval()]
    
    def __str__(self):
        return ", ".join([str(self.expr1), str(self.expr2)])

# multiplies the result of two expressions
class Mul(BinExpr):
    def __init__(self, expr1, expr2):
        super().__init__(expr1, expr2)
    
    def eval(self):
        return self.expr1.eval() * self.expr2.eval()
    
    def __str__(self):
        return f"{self.expr1} * {self.expr2}"

# divides the result of two expressions
class Div(BinExpr):
    def __init__(self, expr1, expr2):
        super().__init__(expr1, expr2)

    def eval(self):
        return self.expr1.eval() / self.expr2.eval()
    
    def __str__(self):
        return f"{self.expr1} / {self.expr2}"

# adds the result of two expressions
class Add(BinExpr):
    def __init__(self, expr1, expr2):
        super().__init__(expr1, expr2)

    def eval(self):
        return self.expr1.eval() + self.expr2.eval()
    
    def __str__(self):
        return f"{self.expr1} + {self.expr2}"

# subtracts the result of two expressions
class Sub(BinExpr):
    def __init__(self, expr1, expr2):
        super().__init__(expr1, expr2)

    def eval(self):
        return self.expr1.eval() - self.expr2.eval()
    
    def __str__(self):
        return f"{self.expr1} - {self.expr2}"
