from functools import reduce
from enum import Enum
import operator
import re

def restoreSplitStrings(l: list):
    if not l:
        return []
    try:
        first = l.index('"')
    except ValueError as _:
        return l
    try:
        nextoccurence = l.index('"', first+1)
    except ValueError as _:
        raise Exception("Syntax Error: String opened but not closed")
    else:
        return l[:first] + [reduce(lambda x, y: x + ' ' + y, l[first:nextoccurence+1])] + restoreSplitStrings(l[nextoccurence+1:])

def genToken(w: str):
    """
    Gets token out of word
    """
    builtins = ["zeg_na", "stel", "stapel", "verklein", "definieer"]
    operators = ["in"]
    if w in builtins:
        return Token("BuiltIn", w)
    if w in operators:
        return Token("Operator", w)
    if w[0] == '"' and w[-1] == '"':
        return Token("String", w)
    if w.isnumeric():
        return Token("Number", w)
    if re.fullmatch("^[a-zA-Z_][a-zA-Z_0-9]*", w) is not None:
        return Token("Identifier", w)
    if w == "lus":
        return Token("LoopStart", w)
    if w == "sul":
        return Token("LoopEnd", w)
    if w == "indien":
        return Token("If", w)
    if w == "neidni":
        return Token("Endif", w)
    else:
        raise Exception("Invalid Syntax: %s" % w)

class Token:
    def __init__(self, type_: str, text_: str):
        self.type = type_
        self.text = text_
    def __repr__(self):
        return "[" + self.type + ", " + self.text + "]"

def lex(filename: str):
    with open(filename) as file: 
        lines = file.readlines()
    # filter out comments
    lines = map(lambda x: x.split("//", 1)[0], lines)
    # generate token list
    tokens = list(filter(None, map(lambda x: list(map(lambda y: genToken(y), x)), map(lambda x: restoreSplitStrings(x), map(lambda x: x.split(), lines)))))
    return tokens