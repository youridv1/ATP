from functools import reduce
import re
from composite import composite_function
from typing import *

class Token:
    def __init__(self, type_: str, text_: str):
        self.type = type_
        self.text = text_
    def __repr__(self):
        return "[" + self.type + ", " + self.text + "]"

def genToken(w: str) -> Token:
    """
    Gets token out of word
    """
    builtins = ["zeg_na", "stel", "stapel", "verklein", "definieer", "produceer", "verdeel"]
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

# TODO: how do you type a decorator?
def ifNotDecorator(func):
    def inner(toLex):
        if not toLex:
            return ("","")
        return func(toLex)
    return inner

@ifNotDecorator
def lexString(toLex: str) -> Tuple[str, str]:
    head, *tail = toLex
    if head != '"':
        string, rest = lexString(tail)
        return (head+string, rest)
    else:
        return (head, tail)

@ifNotDecorator
def lexToken(toLex: str) -> Tuple[str, str]:
    head, *tail = toLex
    if head != " ":
        string, rest = lexToken(tail)
        return (head+string, rest)
    else:
        return ("", tail)

def lexLine(toLex: str) -> Tuple[List[Union[Token, str]], str]:
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

# Didn't know how to define this one with python typing
# But it converts from a recursive list to a regular python list
# [A, [A, [A, []]]] -> [A]
def flatten(t):
    if not t:
        return []
    if len(t) == 1:
        return t[0]
    return [t[0]] + flatten(t[1])

def removeComment(toLex: str) -> str:
    return toLex.split("//", 1)[0]

def myStrip(toLex: str):
    return toLex.strip()

def myHead(a: tuple):
    return a[0]

def genTokens(a: List[str]) -> List[Token]:
    return list(map(lambda x: genToken(x), a))

def emptyLineFilter(a: list) -> List[Token]:
    return filter(None, a)

linesToTokens = composite_function(genTokens, flatten, myHead, lexLine, myStrip, removeComment)

def lex(filename: str) -> List[Token]:
    with open(filename) as file: 
        lines = file.read().replace(";", "\n").split("\n")
    return list(filter(None, map(linesToTokens, lines)))
