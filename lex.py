import re
from composite import composite_function
from typing import *
from error import error

A = NewType('A', int)

class Token:
    def __init__(self, type_: str, text_: str):
        self.type = type_
        self.text = text_
    def __repr__(self):
        return "[" + self.type + ", " + self.text + "]"

# genToken :: str -> Token
def genToken(w: str) -> Token:
    """
    Gets token out of word
    """
    builtins = ["zeg_na", "stel", "stapel", "verklein", "definieer", "produceer", "verdeel"]
    if w in builtins:
        return Token("BuiltIn", w)
    if w[0] == '"' and w[-1] == '"':
        return Token("String", w)
    if w.isnumeric():
        return Token("Number", int(w))
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
    error("Invalid Syntax: %s" % w)

# ifNotDecorator :: (A -> A) -> (str, str)
def ifNotDecorator(func: Callable[[A], A]) -> Tuple[str, str]:
    '''Decorator that checks input is not empty and returns a tuple of two empty strings otherwise'''
    def inner(toLex):
        if not toLex:
            return ("","")
        return func(toLex)
    return inner

@ifNotDecorator
# lexString :: str -> (str, str)
def lexString(toLex: str) -> Tuple[str, str]:
    '''Lex a literal string'''
    head, *tail = toLex
    if head != '"':
        string, rest = lexString(tail)
        return (head+string, rest)
    else:
        return (head, tail)

@ifNotDecorator
# lexToken :: str -> (str, str)
def lexToken(toLex: str) -> Tuple[str, str]:
    '''Lex words to be used by genToken'''
    head, *tail = toLex
    if head != " ":
        string, rest = lexToken(tail)
        return (head+string, rest)
    else:
        return ("", tail)

# lexLine :: str -> ([Token | Str], str)
def lexLine(toLex: str) -> Tuple[List[Union[Token, str]], str]:
    '''Lex a line of code'''
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
# Haskell typing makes no sense either because haskell only uses recursive lists
# flatten :: [A, [A, [A, []]]] -> [A]
def flatten(t):
    '''Flatten a recursive list to a regular python list'''
    if not t:
        return []
    if len(t) == 1:
        return t[0]
    return [t[0]] + flatten(t[1])

# removeComment :: str -> str
def removeComment(toLex: str) -> str:
    '''Remove comments from code before lexing'''
    return toLex.split("//", 1)[0]

# myStrip :: str -> str
def myStrip(toLex: str) -> str:
    '''Strip whitespace'''
    return toLex.strip()

# myHead :: (A, A) -> A
def myHead(a: tuple) -> A:
    '''Returns the first item of a tuple'''
    return a[0]

# genTokens :: [str] -> [Token]
def genTokens(a: List[str]) -> List[Token]:
    '''Loop for genToken'''
    return list(map(lambda x: genToken(x), a))

# emptyLineFilter :: [Token | None] -> [Token]
def emptyLineFilter(a: List[Token | None]) -> List[Token]:
    '''Filters out empty lines'''
    return filter(None, a)

# Composite function
# linesToTokens = genTokens . flatten . myHead . lexLine . myStrip . removeComment
# linesToTokens :: str -> [Token]
linesToTokens = composite_function(genTokens, flatten, myHead, lexLine, myStrip, removeComment)

# lex :: str -> [Token]
def lex(filename: str) -> List[Token]:
    '''Lexes a file to a list of tokens to be used by a parser'''
    with open(f"youriSrc/{filename}") as file: 
        lines = file.read().replace(";", "\n").split("\n")
    return list(filter(None, map(linesToTokens, lines)))
