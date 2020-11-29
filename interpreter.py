from collections import namedtuple
from AST import Expression, Variable, Value, Loop

def interpretLoop(exp: namedtuple, memory: dict):
    if not memory[exp.Variable.name] == exp.Value.content:
        memory = interpret(exp.body, memory)
        return interpretLoop(exp, memory)
    else:
        return memory

def interpretExpression(exp: namedtuple, memory: dict):
    if type(exp) == Loop:
        memory = interpretLoop(exp, memory)
    elif exp.function == "zeg_na":
        print(*map(lambda x: x[2:-2] if '"' in x else memory[x], exp.args))
    elif exp.function == "stel":
        memory[exp.args[0].name] = exp.args[1].content
    elif exp.function == "stapel":
        if type(exp.args[1]) == Value:
            memory[exp.args[0].name] += exp.args[1].content
        else:
            memory[exp.args[0].name] += memory[exp.args[1].name]
    elif exp.function == "verklein":
        memory[exp.args[0].name] -= exp.args[1].content
    else:
        print("Expected BuiltIn or Identifier, got %s" % exp.function)
        return 1
    return memory

def interpret(ast: list, memory = None):
    if memory == None:
        memory = {}
    if len(ast) < 2:
        memory = interpretExpression(ast[0], memory)
    else:
        memory = interpretExpression(ast[0], memory)
        interpret(ast[1:], memory)
    return memory
    