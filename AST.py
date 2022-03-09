from collections import namedtuple
from lex import lex

Expression = namedtuple("Expression", ["function", "argc", "args"])
Variable = namedtuple("Variable", ["name"])
Value = namedtuple("Value", ["content"])
Loop = namedtuple("Loop", ["body", "Variable", "Value"])
If = namedtuple("If", ["body", "LHS", "RHS"])
Function = namedtuple("Function", ["name", "body"])
Call = namedtuple("Call", ["name", "result", "argc", "args"])

def parseStel(tokensLine: list, variables: list):
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
                return Expression("stel", len(tokensLine[1:]), [Variable(tokensLine[1].text), Variable(tokensLine[2].text), Value(int(tokensLine[3].text))]), variables
            else:
                raise Exception("Only tokens of type Number can be used as an index, got %s instead" % tokensLine[3].type)
        else:
            raise Exception("Passing 3 arguments to stel is only allowed when indexing an argument list")             
    else:
        raise Exception("Stel only takes 2 or arguments. (3 when using indexes) %s were given." % len(tokensLine[1:]))

def parseMathStatement(tokensLine: list, variables: list):
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

def parseDefinition(tokensLine: list, variables: list):
    if len(tokensLine) == 3:
        if all(map(lambda x: x.type == "Identifier", tokensLine[1:])):
            tmp = list(filter(lambda x: x[-1] == '~', variables))
            return Function(tokensLine[1].text, parse(lex(tokensLine[2].text + ".yo"), tmp)), variables+[tokensLine[1].text + '~']
        else:
            raise Exception("Definieer expects two Identifiers.Got %s instead" % list(map(lambda x: x.type, tokensLine[1:])))
    else:
        raise Exception("Definieer expects two arguments, a function name and a file name. Got %s instead" % list(map(lambda x: x.text, tokensLine[1:])))

def parseFunctionCall(tokensLine: list, variables: list):
    if tokensLine[0].text + '~' in variables:
        if all(map(lambda x: True if x.type == "String" or x.type == "Number" else (True if x.text in variables else False), tokensLine[2:])):
            if tokensLine[1].type == "Identifier" and tokensLine[1].text == "leeg":
                return Call(tokensLine[0].text, None, len(tokensLine[2:]), list(map(lambda x: Value(x.text) if x.type == "String" or x.type == "Number" else Variable(x.text), tokensLine[2:]))), variables
            elif tokensLine[1].type == "Identifier" and tokensLine[1].text not in variables:
                return Call(tokensLine[0].text, tokensLine[1].text, len(tokensLine[2:]), list(map(lambda x: Value(x.text) if x.type == "String" or x.type == "Number" else Variable(x.text), tokensLine[2:]))), variables+[tokensLine[1].text]
            else:
                raise Exception("Een functie Call verwacht een ongebruikte naam voor de teruggave of 'leeg'")
        else:
            raise Exception("Only strings, numbers or known variable names are allowed as an Argument")
    else:
        raise Exception("Functie niet gedefinieerd")

def parseZegNa(tokensLine: list, variables: list):
    return Expression(("zeg_na"), len(tokensLine[1:]), [Variable(x.text) if x.type == "Identifier" else Value(x.text) for x in tokensLine[1:]]), variables


#TO DO
#Error klasse maken prolly enum 
def parseLine(tokensLine: list, variables: list):
    if tokensLine[0].type == "BuiltIn":
        if tokensLine[0].text == "zeg_na":
            # TO DO:
            # Check if arguments are strings ( all )
            # Implement alternative for when argument is variable name
            # Error thingie
            return parseZegNa(tokensLine, variables)
        # TO DO:
        # Make it so the value of one variable can be assigned to another directly
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
                 

def parseLoop(tokens: list, variables: list):  
    body = parse(tokens[1:-1], variables)
    if len(tokens[-1]) < 2:
        return Loop(body, None, None), variables
    elif len(tokens[-1]) < 3 and tokens[-1][1].type == "Identifier":
        return Loop(body, Variable(tokens[-1][1].text), 0), variables
    elif tokens[-1][1].type == "Identifier" and tokens[-1][2].type == "Number":
        return Loop(body, Variable(tokens[-1][1].text), Value(int(tokens[-1][2].text))), variables
    else:
        if len(tokens[-1]) < 3:
            raise Exception("Sul expects an Identifier, got %s instead." % tokens[-1][1].type)
        else:
            raise Exception("Sul expects an Identifier and a Number, got %s and %s instead." % (tokens[-1][1].type, tokens[-1][2].type))

def parseIf(tokens: list, variables: list):
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


def parse(tokens: list, variables = None):
    if not tokens:
        return []
    if variables == None:
        variables = []
    if tokens[0][0].text == "lus":
        loopLocations = list(map(lambda x: True if x[0].text == "sul" else False, tokens))
        try:
            loopEnd = loopLocations.index(True, 1)
        except ValueError as _:
            raise Exception("Lus opened but not closed.")
        temp, variables = parseLoop(tokens[:loopEnd+1], variables)
        return [temp] + parse(tokens[loopEnd+1:], variables)
    if tokens[0][0].text == "indien":
        endifs = list(map(lambda x: True if x[0].text == "neidni" else False, tokens))
        try:
            end = endifs.index(True, 1)
        except ValueError as _:
            raise Exception("Indien opened but not closed.")
        temp, variables = parseIf(tokens[:end+1], variables)
        return [temp] + parse(tokens[end+1:], variables)
    if len(tokens) < 2:
        temp, _ = parseLine(tokens[0], variables)
        return [temp]
    else:
        temp, variables = parseLine(tokens[0], variables) 
        return [temp] + parse(tokens[1:], variables)
