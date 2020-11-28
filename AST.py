from collections import namedtuple

Expression = namedtuple("Expression", ["function", "argc", "args"])
Variable = namedtuple("Variable", ["name"])
Value = namedtuple("Value", ["content"])

#TO DO
#Error klasse maken prolly enum 
def parseLine(tokensLine: list, variables: list):
    if tokensLine[0].type == "BuiltIn":
        if tokensLine[0].text == "zeg_na":
            # TO DO:
            # Check if arguments are strings ( all )
            # Implement alternative for when argument is variable name
            # Error thingie
            return Expression("zeg_na", len(tokensLine[1:]), list(map(lambda x: x.text, tokensLine[1:]))), variables
        # TO DO:
        # Make it so the value of one variable can be assigned to another directly
        if tokensLine[0].text == "stel":
            if len(tokensLine) == 3:
                if tokensLine[1].type == "Identifier":
                    if tokensLine[2].type == "Number":
                        variables.append(tokensLine[1].text)
                        return Expression("stel", len(tokensLine[1:]),[Variable(tokensLine[1].text), Value(int(tokensLine[2].text))]), variables
                    elif tokensLine[2].type == "String":
                        variables.append(tokensLine[1].text)
                        return Expression("stel", len(tokensLine[1:]),[Variable(tokensLine[1].text), Value(tokensLine[2].text)]), variables
                    else:
                        print("Expected a Number or a String, but got an %s, %s instead." % (tokensLine[2].type, tokensLine[2].text))
                        return 1
                else:
                    print("Expected an Identifier, but got an %s, %s instead." % (tokensLine[0].type, tokensLine[0].text))
                    return 1
            else:
                print("Stel only takes 2 arguments. %s were given." % len(tokensLine[1:]))
                return 1   
        if tokensLine[0].text in ["stapel", "verklein"]:
            if len(tokensLine) == 3:
                if tokensLine[1].type == "Identifier":
                    if tokensLine[1].text in variables:
                        if tokensLine[2].type == "Number":
                            return Expression(tokensLine[0].text, len(tokensLine[1:]),[Variable(tokensLine[1].text), Value(int(tokensLine[2].text))]), variables
                        elif tokensLine[2].type == "Identifier":
                            if tokensLine[1].text in variables:
                                return Expression(tokensLine[0].text, len(tokensLine[1:]),[Variable(tokensLine[1].text), Variable(tokensLine[2].text)]), variables
                            else:
                                print("Unknown variable name: %s" % tokensLine[2].text)
                                return 1
                        else:
                            print("Expected a Number or an Identifier, but got an %s, %s instead." % (tokensLine[2].type, tokensLine[2].text))
                            return 1
                    else:
                        print("Unknown variable name: %s" % tokensLine[1].text)
                        return 1
                else:
                    print("Expected an Identifier, but got an %s, %s instead." % (tokensLine[1].type, tokensLine[1].text))
                    return 1
            else:
                print("Stapel only takes 2 arguments. %s were given." % len(tokensLine[1:]))
                return 1 
    #TO DO: 
    #Parse loops because fuck that
    if tokensLine[0].type == "Identifier":
        if tokensLine[0].text == "lus":
            pass
        if tokensLine[0].text == "sul":
            pass
    
def parse(tokens: list, variables = None):
    if not tokens:
        print("Unexpected: Empty Tokens list")
        return 1
    if variables == None:
        variables = []
    if len(tokens) < 2:
        temp, _ = parseLine(tokens[0], variables)
        return [temp]
    else:
        temp, variables = parseLine(tokens[0], variables) 
        return [temp] + parse(tokens[1:], variables)

