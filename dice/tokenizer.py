import re

tokenizer = re.Scanner([
    (r"d",       lambda tokenizer, token : ("DIE", token)), # die roll, should follow and be followed by NUM
    (r"[0-9]+",  lambda tokenizer, token : ("NUM", token)), # a number
    (r"\*",      lambda tokenizer, token : ("MUL", token)), # multiply
    (r"\+",      lambda tokenizer, token : ("ADD", token)), # add
    (r"\-",      lambda tokenizer, token : ("SUB", token)), # subtract
    (r"/",       lambda tokenizer, token : ("DIV", token)), # divide
    (r"\(",      lambda tokenizer, token : ("RPR", token)), # right paren
    (r"\)",      lambda tokenizer, token : ("LPR", token)), # left paren
    (r"h",       lambda tokenizer, token : ("TOP", token)), # modifies the die roll to only add the highest N results
    (r"\s+", None), # None == skip token.
])

def tokenize(str):
    return tokenizer.scan(str)

# test code
if __name__ == '__main__':
    from .parse import Parser

    results, remainder = tokenizer.scan("4d10 + 3")
    # print the token list
    print(results, remainder)

    parser = parse.Parser(results)
    expr = parser.parse()
    # print the parse tree
    print(expr)
    # print the result
    print(expr.eval())

    print("12/3=4")
    results, remainder = tokenizer.scan("12 / 3")
    parser = parse.Parser(results)
    print(parser.eval())

    print("12-3=9")
    results, remainder = tokenizer.scan("12 - 3")
    parser = parse.Parser(results)
    print(parser.eval())

    print("12+3=15")
    results, remainder = tokenizer.scan("12 + 3")
    parser = parse.Parser(results)
    print(parser.eval())

    print("12*3=36")
    results, remainder = tokenizer.scan("12 * 3")
    parser = parse.Parser(results)
    print(parser.eval())

    print("2 * 4d6h3 + 10")
    results, remainder = tokenizer.scan("2 * 4d6h3 + 10")
    parser = parse.Parser(results)
    expr = parser.parse()
    print(expr)
    print(expr.eval())
