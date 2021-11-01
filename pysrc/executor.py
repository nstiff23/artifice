import re
import parse

tokenizer = re.Scanner([
    (r"d",       lambda tokenizer, token : ("DIE", token)),
    (r"[0-9]+",  lambda tokenizer, token : ("NUM", token)),
    (r"\*",      lambda tokenizer, token : ("MUL", token)),
    (r"\+",      lambda tokenizer, token : ("ADD", token)),
    (r"\-",      lambda tokenizer, token : ("SUB", token)),
    (r"\\",      lambda tokenizer, token : ("DIV", token)),
    (r"\(",      lambda tokenizer, token : ("RPR", token)),
    (r"\)",      lambda tokenizer, token : ("LPR", token)),
    # (r"h",                   lambda tokenizer, token : ("TOP", token)),
    (r"\s+", None), # None == skip token.
])

if __name__ == '__main__':
    results, remainder = tokenizer.scan("3 + 4")
    print(results, remainder)

    parser = parse.Parser(results)
    print(parser.parse())
    print(parser.eval())