from functools import reduce
from enum import Enum
import operator
import re
from composite import composite_function

def genToken(w: str):
    """
    Gets token out of word
    """
    builtins = ["zeg_na", "stel", "stapel", "verklein", "definieer", "produceer"]
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
    raise Exception("Invalid Syntax: %s" % w)

class Token:
    def __init__(self, type_: str, text_: str):
        self.type = type_
        self.text = text_
    def __repr__(self):
        return "[" + self.type + ", " + self.text + "]"

def lexString(toLex: str): # -> (str, str)
    if not toLex:
        return ("","")
    head, *tail = toLex
    if head != '"':
        string, rest = lexString(tail)
        return (head+string, rest)
    else:
        return (head, tail)

def lexToken(toLex: str):
    if not toLex:
        return ("","")
    head, *tail = toLex
    if head != " ":
        string, rest = lexToken(tail)
        return (head+string, rest)
    else:
        return ("", tail)

def lexLine(toLex: str):
    if not toLex:
        return ([],"")
    head, *tail = toLex
    if head.isalnum():
        token, rest = lexToken(toLex)
        string, rest2 = lexLine(rest)
        return ([token,string], rest2)
    elif head == " ":
        string, rest = lexLine("".join(tail))
        return (string, rest)
    elif head == '"':
        string, rest = lexString("".join(tail))
        string2, rest2 = lexLine(rest)
        return ([head+string,string2], rest2)
    return ([], toLex) 

def flatten(t):
    if not t:
        return []
    if len(t) == 1:
        return t[0]
    return [t[0]] + flatten(t[1])

def removeComment(toLex: str):
    return toLex.split("//", 1)[0]

def myStrip(toLex: str):
    return toLex.strip()

def myHead(a: tuple):
    return a[0]

def genTokens(a: list):
    return list(map(lambda x: genToken(x), a))

def emptyLineFilter(a: list):
    return filter(None, a)

linesToTokens = composite_function(genTokens, flatten, myHead, lexLine, myStrip, removeComment)

def lex(filename: str):
    with open(filename) as file: 
        lines = file.read().replace(";", "\n").split("\n")
    return list(filter(None, map(linesToTokens, lines)))
