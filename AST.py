from dataclasses import dataclass
from readline import set_completer
from lex import lex, Token
from typing import *

# Circular type dependency, so commented out.
# My AST contains Functions, Calls, Ifs, Loops and Expressions, but Function and If contain an ASTType
ASTType = List #[Union[Function, Call, If, Loop, Expression]]

@dataclass
class Variable:
    name: str

@dataclass
class Value:
    content: Union[str, int]
@dataclass
class Call:
    name: str
    result: str
    argc: int
    args: List[Value | Variable]

@dataclass
class Expression:
    function: str
    argc: int 
    args: List[Variable | Value]

@dataclass
class Loop:
    body: ASTType
    LHS: Union[Variable, Value]
    RHS: Union[Variable, Value]

@dataclass
class If: # the same as Loop, but needed for patternnmatching
    body: ASTType
    LHS: Union[Variable, Value]
    RHS: Union[Variable, Value]

@dataclass
class Function:
    name: str
    body: ASTType

# parseStel :: [Token] -> [str] -> (Expression, [str])
def parseStel(tokensLine: List[Token], variables: List[str]) -> Tuple[Expression, List[str]]:
    '''Parses a stel expression
    Takes list of known variables
    Returns Expression and new variables'''
    if len(tokensLine) == 3:
        if tokensLine[1].type == "Identifier":
            if tokensLine[2].type == "Number":
                return Expression("stel", len(tokensLine[1:]),[Variable(tokensLine[1].text), Value(int(tokensLine[2].text))]), variables+[tokensLine[1].text]
            elif tokensLine[2].type == "String":
                return Expression("stel", len(tokensLine[1:]),[Variable(tokensLine[1].text), Value(tokensLine[2].text)]), variables+[tokensLine[1].text]
            elif tokensLine[2].type == "Identifier":
                    if tokensLine[2].text in variables:
                        return Expression("stel", len(tokensLine[1:]),[Variable(tokensLine[1].text), Variable(tokensLine[2].text)]), variables+[tokensLine[1].text]   
                    else:
                        raise Exception("Unknown variable name: %s" % tokensLine[2].text)
            else:
                raise Exception("Expected a Number or a String, but got an %s, %s instead." % (tokensLine[2].type, tokensLine[2].text))
        else:
            raise Exception("Expected an Identifier, but got an %s, %s instead." % (tokensLine[0].type, tokensLine[0].text))
    elif len(tokensLine) == 4:
        if tokensLine[2].text == "args":
            if tokensLine[3].type == "Number":
                # TO DO:
                # check if name is identifier
                return Expression("stel", len(tokensLine[1:]), [Variable(tokensLine[1].text), Variable(tokensLine[2].text), Value(int(tokensLine[3].text))]), variables+[tokensLine[1].text]
            else:
                raise Exception("Only tokens of type Number can be used as an index, got %s instead" % tokensLine[3].type)
        else:
            raise Exception("Passing 3 arguments to stel is only allowed when indexing an argument list")             
    else:
        raise Exception("Stel only takes 2 or arguments. (3 when using indexes) %s were given." % len(tokensLine[1:]))

# parseMathStatement :: [Token] -> [str] -> (Expression, [str])
def parseMathStatement(tokensLine: List[Token], variables: List[str]) -> Tuple[Expression, List[str]]:
    '''Parses a math statement
    Takes a list of known variables
    Returns an expression and new variables'''
    if len(tokensLine) == 3:
        if tokensLine[1].type == "Identifier":
            if tokensLine[1].text in variables:
                if tokensLine[2].type == "Number":
                    return Expression(tokensLine[0].text, len(tokensLine[1:]),[Variable(tokensLine[1].text), Value(int(tokensLine[2].text))]), variables
                elif tokensLine[2].type == "Identifier":
                    if tokensLine[2].text in variables:
                        return Expression(tokensLine[0].text, len(tokensLine[1:]),[Variable(tokensLine[1].text), Variable(tokensLine[2].text)]), variables
                    else:
                        raise Exception("Unknown variable name: %s" % tokensLine[2].text)   
                else:
                    raise Exception("Expected a Number or an Identifier, but got an %s, %s instead." % (tokensLine[2].type, tokensLine[2].text))    
            else:
                raise Exception("Unknown variable name: %s" % tokensLine[1].text) 
        else:
            raise Exception("Expected an Identifier, but got an %s, %s instead." % (tokensLine[1].type, tokensLine[1].text))
    else:
        raise Exception("Stapel only takes 2 arguments. %s were given." % len(tokensLine[1:]))

# parseDefinition :: [Token] -> [str] -> (Function, [str])
def parseDefinition(tokensLine: List[Token], variables: List[str]) -> Tuple[Function, List[str]]:
    '''Parses a function definition
    Takes a list of known variables
    Returns a Function and new variables'''
    if len(tokensLine) == 3:
        if all(map(lambda x: x.type == "Identifier", tokensLine[1:])):
            tmp = list(filter(lambda x: x[-1] == '~', variables))
            return Function(tokensLine[1].text, parse(lex(tokensLine[2].text + ".yo"), tmp)), variables+[tokensLine[1].text + '~']
            #maybe dont call lexer here 
        else:
            raise Exception("Definieer expects two Identifiers.Got %s instead" % list(map(lambda x: x.type, tokensLine[1:])))
    else:
        raise Exception("Definieer expects two arguments, a function name and a file name. Got %s instead" % list(map(lambda x: x.text, tokensLine[1:])))

# parseFunctionCall :: [Token] -> [str] -> (Call, [str])
def parseFunctionCall(tokensLine: List[Token], variables: List[str]) -> Tuple[Call, List[str]]:
    '''Parses a Call
    Takes a list of known variables
    Returns a Call and new variables'''
    if all(map(lambda x: True if x.type == "String" or x.type == "Number" else (True if x.text in variables else False), tokensLine[2:])):
        if tokensLine[1].type == "Identifier" and tokensLine[1].text == "leeg":
            return Call(tokensLine[0].text, None, len(tokensLine[2:]), list(map(lambda x: Value(x.text) if x.type == "String" or x.type == "Number" else Variable(x.text), tokensLine[2:]))), variables
        elif tokensLine[1].type == "Identifier" and tokensLine[1].text not in variables:
            return Call(tokensLine[0].text, tokensLine[1].text, len(tokensLine[2:]), list(map(lambda x: Value(x.text) if x.type == "String" or x.type == "Number" else Variable(x.text), tokensLine[2:]))), variables+[tokensLine[1].text]
        else:
            raise Exception("Een functie Call verwacht een ongebruikte naam voor de teruggave of 'leeg'")
    else:
        raise Exception("Only strings, numbers or known variable names are allowed as an Argument")

# parseZegNa :: [Token] -> [str] -> (Expression, [str])
def parseZegNa(tokensLine: List[Token], variables: List[str]) -> Tuple[Expression, List[str]]:
    '''Parses a zeg_na expression
    Takes a list of known variables
    Returns a zeg_na expression and new variables'''
    return Expression(("zeg_na"), len(tokensLine[1:]), [Variable(x.text) if x.type == "Identifier" else Value(x.text) for x in tokensLine[1:]]), variables

# parseLine :: [Token] -> [str] -> (Expression | Call | Function, [str])
def parseLine(tokensLine: List[Token], variables: List[str]) -> Tuple[Union[Expression, Call, Function], List[str]]:
    '''Parses a line of code that is in the language
    Takes a list of known variables
    Returns a tuple of either and Expression, Call or Function and new variables
    '''
    if tokensLine[0].type == "BuiltIn":
        if tokensLine[0].text == "zeg_na":
            return parseZegNa(tokensLine, variables)
        if tokensLine[0].text == "stel":
            return parseStel(tokensLine, variables)   
        elif tokensLine[0].text in ["stapel", "verklein", "verdeel", "produceer"]:
            return parseMathStatement(tokensLine, variables)
        elif tokensLine[0].text == "definieer":
            return parseDefinition(tokensLine, variables)
    elif tokensLine[0].type == "Identifier":
        return parseFunctionCall(tokensLine, variables)
    else:
        raise Exception("First token can only be of type BuiltIn or Identifier")
                 
# parseLoop :: [Token] -> [str] -> (Loop, [str])
def parseLoop(tokens: List[Token], variables: List[str]) -> Tuple[Loop, List[str]]:
    '''Parses a Loop Expression
    Takes a list of known variables
    Returns a tuple of a Loop and variables'''  
    body = parse(tokens[1:-1], variables)
    if len(tokens[-1]) < 2:
        return Loop(body, None, None), variables
    elif len(tokens[-1]) < 3 and tokens[-1][1].type == "Identifier":
        return Loop(body, Variable(tokens[-1][1].text), Value(0)), variables
    elif tokens[-1][1].type == "Identifier" and tokens[-1][2].type == "Number":
        return Loop(body, Variable(tokens[-1][1].text), Value(int(tokens[-1][2].text))), variables
    elif tokens[-1][1].type == "Identifier" and tokens[-1][2].type == "Identifier":
        return Loop(body, Variable(tokens[-1][1].text), Variable(tokens[-1][2].text)), variables
    else:
        if len(tokens[-1]) < 3:
            raise Exception("Sul expects an Identifier, got %s instead." % tokens[-1][1].type)
        else:
            raise Exception("Sul expects an Identifier and a Number, got %s and %s instead." % (tokens[-1][1].type, tokens[-1][2].type))

# parseIf :: [Token] -> [str] -> (If, [str])
def parseIf(tokens: List[Token], variables: List[str]) -> Tuple[If, List[str]]:
    '''Parses an If Expression
    Takes a list of known variables
    Returns a tuple of an If and variables'''
    body = parse(tokens[1:-1], variables) 
    if len(tokens[0]) == 3:
        if tokens[0][1].type == "Identifier":
            if tokens[0][1].text in variables:
                LHS = Variable(tokens[0][1].text)
        elif tokens[0][1].type == "Number":
                LHS = Value(tokens[0][1].text)
        else:
            raise Exception("First type must be identifier or number")
        if tokens[0][2].type == "Identifier":
            if tokens[0][2].text in variables:
                RHS = Variable(tokens[0][2].text)
        elif tokens[0][2].type == "Number":
                RHS = Value(tokens[0][2].text)
        else:
            raise Exception("Second type must be identifier or number")
        return If(body, LHS, RHS), variables
    else:
        raise Exception("If needs two arguments to compare")

def scopeEndFind(tokens, keyWord, scopeCounter = 1):
    if not tokens:
        return -1
    match keyWord:
        case "lus":
            endword = "sul"
        case "indien":
            endword = "neidni"

    if tokens[0][0].text == endword:
        scopeCounter -= 1
    elif tokens[0][0].text == keyWord:
        scopeCounter += 1

    if not scopeCounter:
        return 1
    else:
        tmp = scopeEndFind(tokens[1:], keyWord, scopeCounter)
        if tmp == -1:
            return -1
        return 1 + tmp
    
    

# parse :: [Token] -> [str] -> ASTType
def parse(tokens: List[Token], variables: List[str] = None) -> ASTType:
    '''Main parse function
    Takes a list of known variables (Used for parsing functions with parameters)
    Returns an ASTType'''
    if not tokens:
        return []
    if not variables:
        variables = []
    if tokens[0][0].text == "lus":
        loopEnd = scopeEndFind(tokens[1:], "lus")

        temp, variables = parseLoop(tokens[:loopEnd+1], variables)
        return [temp] + parse(tokens[loopEnd+1:], variables)
    if tokens[0][0].text == "indien":
        end = scopeEndFind(tokens[1:], "indien")

        temp, variables = parseIf(tokens[:end+1], variables)
        return [temp] + parse(tokens[end+1:], variables)
    if len(tokens) < 2:
        temp, _ = parseLine(tokens[0], variables)
        return [temp]
    else:
        temp, variables = parseLine(tokens[0], variables) 
        return [temp] + parse(tokens[1:], variables)
