import re
import parse

tokenizer = re.Scanner([
    (r"d",       lambda tokenizer, token : ("DIE", token)), # die roll, should follow and be followed by NUM
    (r"[0-9]+",  lambda tokenizer, token : ("NUM", token)), # a number
    (r"\*",      lambda tokenizer, token : ("MUL", token)), # multiply
    (r"\+",      lambda tokenizer, token : ("ADD", token)), # add
    (r"\-",      lambda tokenizer, token : ("SUB", token)), # subtract
    (r"\\",      lambda tokenizer, token : ("DIV", token)), # divide
    (r"\(",      lambda tokenizer, token : ("RPR", token)), # right paren
    (r"\)",      lambda tokenizer, token : ("LPR", token)), # left paren
    # (r"h",                   lambda tokenizer, token : ("TOP", token)),
    (r"\s+", None), # None == skip token.
])

# test code
if __name__ == '__main__':
    results, remainder = tokenizer.scan("3 + 4")
    print(results, remainder)

    parser = parse.Parser(results)
    print(parser.parse())
    print(parser.eval())