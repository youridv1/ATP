from collections import namedtuple
from AST import Expression, Variable, Value, Loop, Function, Call

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
        print(*map(lambda x: x[2:-2] if '"' in x else (memory[x] if type(memory[x]) == int else memory[x][2:-2]), exp.args))
    elif exp.function == "stel":
        memory[exp.args[0].name] = exp.args[1].content
    elif exp.function == "stapel":
        if type(exp.args[1]) == Value:
            if type(memory[exp.args[0].name]) == type(exp.args[1].content):
                memory[exp.args[0].name] += exp.args[1].content
            else:
                raise Exception("Stapel only works with equal types, not %s and %s" % (type(memory[exp.args[0].name]), type(exp.args[1].content)))
        else:
            if type(memory[exp.args[0].name]) == type(memory[exp.args[1].name]):
                memory[exp.args[0].name] += memory[exp.args[1].name]
            else:
                raise Exception("Stapel only works with equal types, not %s and %s" % (type(memory[exp.args[0].name]), type(memory[exp.args[1].name])))
    elif exp.function == "verklein":
        if type(memory[exp.args[0].name]) == int and type(exp.args[1].content) == int:
            memory[exp.args[0].name] -= exp.args[1].content
        else:
            raise Exception("Verklein only works with int, not %s and %s" % (type(memory[exp.args[0].name]), type(exp.args[1].content)))
    elif type(exp) == Function:
        memory[exp.name] = exp.body
        return memory
    else:
        raise Exception("Expected BuiltIn or Identifier, got %s" % exp.function)
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
    