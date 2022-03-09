from lex import lex
from AST import Expression, Variable, Value, Loop, Function, Call, If, parse
import sys

sys.setrecursionlimit(20000)  # core dumped at 21804

def beginFile():
    return ".cpu cortex-m0\n.align 2\n.text\n.global youriMain\nyouriMain:\n"

def valueToRegister(value: Value, memory: dict, allRegisters: list): # puts an inline value in an available register 
  register = [x for x in allRegisters if x not in memory.values()][0]
  func, sign = ("mov", "#") if value.content < 256 else ("ldr", "=")
  assembly = f"{func} {register}, {sign}{value.content}\n"
  memory[value.content] = register
  return assembly, memory

def compileZegNa(toCompile, memory):
    f = lambda x: f"mov r0, {memory[x.name]}\nbl printlnInteger\n" if type(x) == Variable else "oh fuck"
    return "".join([f(x) for x in toCompile.args]), memory

# Returns string of assembly needed for this statement
def compileExpression(toCompile: Expression, memory):
    allRegisters = ["r1", "r2", "r3", "r4", "r5", "r6", "r7"]
    funcToAssem = {"produceer":"mul", "stapel":"add", "verklein":"sub"}
    match toCompile.function:
        case a if a in funcToAssem.keys():
            if type(toCompile.args[1]) == Value:
                memAssem, memory = valueToRegister(toCompile.args[1], memory, allRegisters)
                snd = memory[toCompile.args[1].content]
            else: # variable
                # for now we assume nothing ends up in memory and everything fits into registers
                memAssem = ""
                snd = memory[toCompile.args[1].name]
            return memAssem + f"{funcToAssem[a]} {memory[toCompile.args[0].name]}, {snd}, {memory[toCompile.args[0].name]}\n", memory # "memory" will store the location of the data, so a register name or a memory address
        case "stel":
            if type(toCompile.args[1]) == Value:
                func, sign = ("mov", "#") if toCompile.args[1].content < 256 else ("ldr", "=")
                immed = sign + str(toCompile.args[1].content)
                register = [x for x in allRegisters if x not in memory.values()][0]
                memory[toCompile.args[0].name] = register
                return f"{func} {register}, {immed}\n", memory
        case "zeg_na":
            return compileZegNa(toCompile, memory)
        case _:
            print(":(")
            return


def compile(ast: list, memory: dict = {}):
    assembly, memory = compileExpression(ast[0], memory)
    assembly2 = ""
    if rest := ast[1:]:
        assembly2, memory = compile(rest, memory)
    return assembly+assembly2, memory


def mainCompiler(fileName: str):
    fileBegin = beginFile()
    push = "push { r1, r2, r3, r4, r5, r6, r7, lr }\n"
    pop = "pop { r1, r2, r3, r4, r5, r6, r7, pc }\n"
    x = parse(lex(f"{fileName}.yo"))
    compiledCode, _ = compile(x)
    print(x)
    with open(f"{fileName}.S", 'w') as f:
        f.write(fileBegin + push + compiledCode + pop)

if __name__ == "__main__":
    fileName = "actuallyhelloworld"
    mainCompiler(fileName)
