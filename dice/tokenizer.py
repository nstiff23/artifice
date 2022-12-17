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
