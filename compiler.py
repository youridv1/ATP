from lex import lex
from AST import Expression, Variable, Value, Loop, Function, Call, If, parse
import sys

sys.setrecursionlimit(20000)  # core dumped at 21804

def beginFile():
    return

# Returns string of assembly needed for this statement
def compileExpression(toCompile: Expression, memory):
    allRegisters = ["r1", "r2", "r3", "r4", "r5", "r6", "r7"]
    match toCompile.function:
        case "produceer":
            if type(toCompile.args[1]) == Value: 
                return "mul %s %s\n" % (memory[toCompile.args[0].name], "r2"), memory # need to figure out some kind of way to manage registers
            else: # variable
                # for now we assume nothing ends up in memory and everything fits into registers
                return "mul %s %s\n" % (memory[toCompile.args[0].name], memory[toCompile.args[1].name]), memory # "memory" will store the location of the data, so a register name or a memory address
        case "stel":
            if type(toCompile.args[1]) == Value:
                immed = "=immed" + str(toCompile.args[1].content)
                register = [x for x in allRegisters if x not in memory.values()][0]
                memory[toCompile.args[0].name] = register
                return "ldr %s %s\n" % (register, immed), memory
        case _:
            print(":(")
            return


def compile(ast: list, memory: dict = {}):
    assembly, memory = compileExpression(ast[0], memory)
    assembly2 = ""
    if rest := ast[1:]:
        assembly2, memory = compile(rest, memory)
    return assembly+assembly2, memory


def mainCompiler():
    x = parse(lex("actuallyhelloworld.yo"))
    assembly, _ = compile(x)
    print(x)
    print(assembly)

if __name__ == "__main__":
    mainCompiler()
