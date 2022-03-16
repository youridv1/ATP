from lex import lex
from AST import Expression, Variable, Value, Loop, Function, Call, If, parse
import sys

sys.setrecursionlimit(20000)  # core dumped at 21804

def beginFile(dataSegment = ""):
    return f".cpu cortex-m0\n.align 2\n\n{dataSegment}.text\n.global youriMain\n\nyouriMain:\n"

def valueToRegister(value: Value, memory: dict, allRegisters: list): # puts an inline value in an available register 
  register = [x for x in allRegisters if x not in memory.values()][0]
  func, sign = ("mov", "#") if value.content < 256 else ("ldr", "=")
  assembly = f"{func} {register}, {sign}{value.content}\n"
  memory[value.content] = register
  return assembly, memory

def stringToR0(value: Value, data: dict):
  key = f"LIT{len(data)}"
  data[key] = value.content
  assembly = f"ldr r0, ={key}\n"
  return assembly, data

def intToR0(value):
  content = int(value.content)
  func, sign = ("mov", "#") if content < 256 else ("ldr", "=")
  assembly = f"{func} r0, {sign}{content}\n"
  return assembly

def ZegNaHelper(arg, memory, data):
    match arg:
        case arg if type(arg) == Variable:
            return f"mov r0, {memory[arg.name]}\nbl printlnInteger\n", memory, data
        case arg if type(arg) == Value:
            if '"' in arg.content:
              assembly, data = stringToR0(arg, data)
              return assembly+"bl printlnStr\n", memory, data
            assembly = intToR0(arg)
            return assembly+"bl printlnInteger\n", memory, data
            

def compileZegNa(toCompile, memory, data):
    assembly, memory, data = ZegNaHelper(toCompile.args[0], memory, data)
    assembly2 = ""
    if rest := toCompile.args[1:]:
        assembly2, memory, data = compileZegNa(Expression("zeg_na", len(rest), rest), memory, data)
    return assembly+assembly2, memory, data

# Returns string of assembly needed for this statement
def compileExpression(toCompile: Expression, memory, data):
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
            return memAssem + f"{funcToAssem[a]} {memory[toCompile.args[0].name]}, {snd}, {memory[toCompile.args[0].name]}\n", memory, data # "memory" will store the location of the data, so a register name or a memory address
        case "stel":
            if type(toCompile.args[1]) == Value:
                  func, sign = ("mov", "#") if toCompile.args[1].content < 256 else ("ldr", "=")
                  immed = sign + str(toCompile.args[1].content)
                  register = [x for x in allRegisters if x not in memory.values()][0]
                  memory[toCompile.args[0].name] = register
                  return f"{func} {register}, {immed}\n", memory, data
        case "zeg_na":
            return compileZegNa(toCompile, memory, data)
        case _:
            print(":(")
            return

def compileData(data):
  helper = lambda x, y: f"{x}: .asciz {y}\n"
  bruh = [helper(key, value) for key, value in data.items()]
  return ".data\n\n" + "".join(bruh) + "\n"


def compile(ast: list, memory: dict = {}, data: dict = {}):
    assembly, memory, data = compileExpression(ast[0], memory, data)
    assembly2 = ""
    if rest := ast[1:]:
        assembly2, memory, data = compile(rest, memory, data)
    return assembly+assembly2, memory, data


def mainCompiler(fileName: str):
    push = "push { r1, r2, r3, r4, r5, r6, r7, lr }\n"
    pop = "pop { r1, r2, r3, r4, r5, r6, r7, pc }\n"
    x = parse(lex(f"{fileName}.yo"))
    compiledCode, _, data = compile(x)
    print(x)
    print(data)
    dataSegment = compileData(data)
    fileBegin = beginFile(dataSegment)
    with open(f"{fileName}.S", 'w') as f:
        f.write(fileBegin + push + compiledCode + pop)

if __name__ == "__main__":
    fileName = "actuallyhelloworld"
    mainCompiler(fileName)
