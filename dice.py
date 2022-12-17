from dice import Parser
from dice import tokenize

# test code for the dice package
# not used by the bot

if __name__ == '__main__':
    results, remainder = tokenize("4d10 + 3")
    # print the token list
    print(results, remainder)

    parser = Parser(results)
    expr = parser.parse()
    # print the parse tree
    print(expr)
    # print the result
    print(expr.eval())

    print("12/3=4")
    results, remainder = tokenize("12 / 3")
    parser = Parser(results)
    assert(parser.eval() == 4)

    print("12-3=9")
    results, remainder = tokenize("12 - 3")
    parser = Parser(results)
    assert(parser.eval() == 9)

    print("12+3=15")
    results, remainder = tokenize("12 + 3")
    parser = Parser(results)
    assert(parser.eval() == 15)

    print("12*3=36")
    results, remainder = tokenize("12 * 3")
    parser = Parser(results)
    assert(parser.eval() == 36)

    print("2 * 4d6h3 + 10")
    results, remainder = tokenize("2 * 4d6h3 + 10")
    parser = Parser(results)
    expr = parser.parse()
    print(expr)
    print(expr.eval())