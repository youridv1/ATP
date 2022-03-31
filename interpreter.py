from collections import namedtuple
from AST import Expression, Variable, Value, Loop, Function, Call, If
import operator as op

def interpretLoop(exp: namedtuple, memory: dict):
    if not memory[exp.Variable.name] == exp.Value.content:
        memory = interpret(exp.body, memory)
        return interpretLoop(exp, memory)
    else:
        return memory

def interpretIf(exp: namedtuple, memory: dict):
    extractor = lambda x: int(x.content) if type(x) == Value else int(memory[x.name])
    LHS = extractor(exp.LHS)
    RHS = extractor(exp.RHS)
    if LHS == RHS:
        memory = interpret(exp.body, memory)
    return memory

def interpretCall(exp, memory):
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

def interpretStel(exp, memory):
    if exp.argc == 2:
        if type(exp.args[1]) == Value:
            memory[exp.args[0].name] = exp.args[1].content
        else:
            memory[exp.args[0].name] = memory[exp.args[1].name]
    elif exp.argc == 3:
        memory[exp.args[0].name] = memory["args"][exp.args[2].content]
    return memory

def interpretMath(exp, memory, op):
    if type(exp.args[1]) == Value:
        if type(memory[exp.args[0].name]) == type(exp.args[1].content):
            memory[exp.args[0].name] = op(memory[exp.args[0].name], exp.args[1].content)
        else:
            raise Exception("Math only works with equal types, not %s and %s" % (type(memory[exp.args[0].name]), type(exp.args[1].content)))
    else:
        if type(memory[exp.args[0].name]) == type(memory[exp.args[1].name]):
            memory[exp.args[0].name] = op(memory[exp.args[0].name], memory[exp.args[1].name])
        else:
            raise Exception("Math only works with equal types, not %s and %s" % (type(memory[exp.args[0].name]), type(memory[exp.args[1].name])))
    return memory

def myPrint(exp, memory):
    print(*map(lambda x: x.content[1:-1] if type(x) == Value and '"' in x.content else (
        memory[x.name] if type(memory[x.name]) == int else memory[x.name][1:-1]), exp.args))
    return memory

def interpretFunction(exp, memory):
    memory[exp.name] = exp.body
    return memory


def interpretExpression(exp: namedtuple, memory: dict):
    match exp:
        case If(_, _, _):      return interpretIf(exp, memory)
        case Loop(_, _, _):    return interpretLoop(exp, memory)
        case Call(_, _, _, _): return interpretCall(exp, memory)
        case Function(_, _):   return interpretFunction(exp, memory)
        case Expression("zeg_na", _, _):    return myPrint(exp, memory)
        case Expression("stel", _, _):      return interpretStel(exp, memory)
        case Expression("stapel", _, _):    return interpretMath(exp, memory, op.add)
        case Expression("verklein", _, _):  return interpretMath(exp, memory, op.sub)
        case Expression("produceer", _, _): return interpretMath(exp, memory, op.mul)
        case Expression("verdeel", _, _):   return interpretMath(exp, memory, op.floordiv)
        case _: raise Exception("Expected BuiltIn or Identifier, got %s" % exp.function)

def interpret(ast: list, memory = None):
    if not memory:
        memory = {}
    if len(ast) < 2:
        memory = interpretExpression(ast[0], memory)
    else:
        memory = interpretExpression(ast[0], memory)
        interpret(ast[1:], memory)
    return memory
    