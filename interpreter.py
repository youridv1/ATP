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
    elif type(exp) == Function:
        memory[exp.name] = exp.body
        return memory
    elif type(exp) == Call:
        if exp.name in memory:
            if exp.result == None: 
                args = {"args" : list(map(lambda x: x.content if type(x) == Value else memory[x.name], exp.args))}
                tmp = dict(filter(lambda x: type(x[1]) == list and x[0] != "args", memory.items()))
                args = {**args, **tmp}
                interpret(memory[exp.name], args)
                return memory
            else:
                args = {"args" : list(map(lambda x: x.content if type(x) == Value else memory[x.name], exp.args))}
                tmp = dict(filter(lambda x: type(x[1]) == list and x[0] != "args", memory.items()))
                args = {**args, **tmp}
                temp = interpret(memory[exp.name], args)
                memory[exp.result] = temp["result"]
                return memory
        else:
            raise Exception("Onbekende functie. Eerst Definieren")
    elif exp.function == "zeg_na":
        print(*map(lambda x: x[2:-2] if '"' in x else (memory[x] if type(memory[x]) == int else memory[x][2:-2]), exp.args))
    elif exp.function == "stel":
        if exp.argc == 2:
            memory[exp.args[0].name] = exp.args[1].content
        elif exp.argc == 3:
            memory[exp.args[0].name] = memory["args"][exp.args[2].content]
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
    