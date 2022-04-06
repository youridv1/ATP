from collections import *
from AST import Expression, Variable, Value, Loop, Function, Call, If, ASTType
import operator as op
from typing import *

MemType = Dict[str, Union[str, int, List[Union[Function, Call, If, Loop, Expression]], List[Union[str, int]]]]
InterpretType = Union[If, Loop, Call, Function, Expression]

# interpretLoop :: InterpretType -> MemType -> MemType
def interpretLoop(exp: InterpretType, memory: MemType) -> MemType:
    '''Interpret a loop and return new memory'''
    if not memory[exp.Variable.name] == exp.Value.content:
        memory = interpret(exp.body, memory)
        return interpretLoop(exp, memory)
    else:
        return memory

# interpretIf :: If -> MemType -> MemType
def interpretIf(exp: If, memory: MemType) -> MemType:
    '''Interpret an If and return new memory'''
    extractor = lambda x: int(x.content) if type(x) == Value else int(memory[x.name])
    LHS = extractor(exp.LHS)
    RHS = extractor(exp.RHS)
    if LHS == RHS:
        memory = interpret(exp.body, memory)
    return memory

# interpretCall :: Call -> MemType -> MemType
def interpretCall(exp: Call, memory: MemType) -> MemType:
    '''Interpret a function call and return new memory'''
    if exp.name in memory:
        args = {"args" : list(map(lambda x: x.content if type(x) == Value else memory[x.name], exp.args))}
        tmp = dict(filter(lambda x: type(x[1]) == list and x[0] != "args", memory.items()))
        args = {**args, **tmp}
        temp = interpret(memory[exp.name], args)
        if exp.result: 
            memory[exp.result] = temp["result"]
        return memory
    else:
        raise Exception("Onbekende functie. Eerst Definieren")

# interpretStel :: Expression -> MemType -> MemType
def interpretStel(exp: Expression, memory: MemType) -> MemType:
    '''Interpret a stel expression (assignment) and return new memory'''
    if exp.argc == 2:
        if type(exp.args[1]) == Value:
            memory[exp.args[0].name] = exp.args[1].content
        else:
            memory[exp.args[0].name] = memory[exp.args[1].name]
    elif exp.argc == 3:
        memory[exp.args[0].name] = memory["args"][exp.args[2].content]
    return memory

# interpretMath :: Expression -> MemType -> (int -> int -> int) -> MemType
def interpretMath(exp: Expression, memory: MemType, op: Callable[[int, int], int]) -> MemType:
    '''Interpret a math expression and return new memory'''
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

# myPrint :: Expression -> MemType -> None
def myPrint(exp: Expression, memory: MemType) -> None:
    '''Print an Expression to terminal'''
    print(*map(lambda x: x.content[1:-1] if type(x) == Value and '"' in x.content else (
        memory[x.name] if type(memory[x.name]) == int else memory[x.name][1:-1]), exp.args))

# interpretFunction :: Function -> MemType -> MemType
def interpretFunction(exp: Function, memory: MemType) -> MemType:
    '''Interpret a function definition and return new memory'''
    memory[exp.name] = exp.body
    return memory

# interpretExpression :: InterpretType -> MemType -> MemType
def interpretExpression(exp: InterpretType, memory: MemType) -> MemType:
    '''Interpret any expression by pattern matching and calling the appropriate function
    Return new memory'''
    match exp:
        case If(_, _, _):      return interpretIf(exp, memory)
        case Loop(_, _, _):    return interpretLoop(exp, memory)
        case Call(_, _, _, _): return interpretCall(exp, memory)
        case Function(_, _):   return interpretFunction(exp, memory)
        case Expression("zeg_na", _, _):    myPrint(exp, memory); return memory
        case Expression("stel", _, _):      return interpretStel(exp, memory)
        case Expression("stapel", _, _):    return interpretMath(exp, memory, op.add)
        case Expression("verklein", _, _):  return interpretMath(exp, memory, op.sub)
        case Expression("produceer", _, _): return interpretMath(exp, memory, op.mul)
        case Expression("verdeel", _, _):   return interpretMath(exp, memory, op.floordiv)
        case _: raise Exception("Expected BuiltIn or Identifier, got %s" % exp.function)

# interpet :: ASTType -> MemType -> MemType
def interpret(ast: ASTType, memory: MemType = None) -> MemType:
    '''Main interpreter function
    Interpret an ASTType and return final memory'''
    if not memory:
        memory = {}
    memory = interpretExpression(ast[0], memory)
    if rest := ast[1:]:
        memory = interpret(rest, memory)
    return memory
    