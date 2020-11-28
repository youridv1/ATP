from functools import reduce
from enum import Enum
import operator
import re

def recLast(l : list):
    """
    returns index of last string with last character '"'
    """
    # print(l)
    if not l:
        return -1
    if l[-1][-1] == '"':
        return len(l) - 1 
    else:
        return recLast(l[:-1])

def recFirst(l : list):
    """
    returns index of last string with first character '"'
    """
    if not l:
        return -1
    if l[-1][0] == '"':
        return len(l) - 1 
    else:
        return recFirst(l[:-1])

def restoreSplitStrings(l : list):
    """
    finds split up strings and restores them
    """
    if not l:
        return []
    if recFirst(l) >= 0:
        if recFirst(l) < recLast(l):
            return restoreSplitStrings(l[:recFirst(l)]) + [str(reduce(lambda x, y: x+' '+y, l[recFirst(l):recLast(l)+1]))] + l[recLast(l)+1:]
        if recFirst(l) == recLast(l):
            return restoreSplitStrings(l[:recFirst(l)]) + [l[recLast(l)]] + l[recLast(l)+1:]
        if recFirst(l) > recLast(l):
            raise Exception("Syntax Error: String opened but not closed")
    else:
        return l

def genToken(w: str):
    """
    Gets token out of word
    """
    builtins = ["zeg_na", "stel", "stapel", "verklein"]
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
    if w == "lus":
        return Token("LoopEnd", w)
    else:
        raise Exception("Fuck moet ik hier mee, ouwe: " + w)

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