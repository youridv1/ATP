from collections import namedtuple

Expression = namedtuple("Expression", ["function", "argc", "args"])


def parse(tokens: list):
    if tokens[0].type == "BuiltIn":
        if tokens[0].text == "zeg_na":
            # TO DO:
            # Check if arguments are strings ( all )
            return Expression("zeg_na", len(tokens[1:]), list(map(lambda x: x.text, tokens[1:])))
        if tokens[0].text == "stel":
            pass
        if tokens[0].text == "stapel":
            pass
        if tokens[0].text == "verklein":
            pass
    if tokens[0].type == "Identifier":
        if tokens[0].text == "lus":
            pass
        if tokens[0].text == "sul":
            pass