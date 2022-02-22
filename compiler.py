from lex import lex
from AST import Expression, Variable, Value, Loop, Function, Call, If, parse
import sys

sys.setrecursionlimit(20000)  # core dumped at 21804

def beginFile():
    return

# Returns string of assembly needed for this statement
def compileExpression(toCompile: Expression, memory):
    match toCompile.function:
        case "produceer":
            if type(toCompile.args[1]) == Value:
                if type(memory[toCompile.args[0].name]) == int and type(toCompile.args[1].content) == int:
                    # assembly goes here 
                    return "mul %s %s" % "r1", "r2"
                else:
                    raise Exception("produceer only works with int")
            else:
                if type(memory[toCompile.args[0].name]) == int and type(memory[toCompile.args[1].name]) == int:
                    # assembly goes here
                    return
                else:
                    raise Exception("produceer only works with int, not %s and %s" % (type(memory[toCompile.args[0].name]), type(toCompile.args[1].content)))
        case _:
            print(":(")
            return





def mainCompiler():
    x = parse(lex("actuallyhelloworld.yo"))
    print(x)

if __name__ == "__main__":
    mainCompiler()
