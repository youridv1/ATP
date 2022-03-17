from lex import lex
from AST import Expression, Variable, Value, Loop, Function, Call, If, parse
import sys

sys.setrecursionlimit(20000)  # core dumped at 21804


def beginFile(dataSegment=""):
    return f".cpu cortex-m0\n.align 2\n\n{dataSegment}.text\n.global youriMain\n\nyouriMain:\n"


def getRegister(allRegisters, memory):
    return [x for x in allRegisters if x.lower() not in memory.values() and x.upper() not in memory.values()][0]


# puts an inline value in an available register
def valueToRegister(value: Value, memory: dict, allRegisters: list):
    register = getRegister(allRegisters, memory)
    func, sign = ("mov", "#") if value.content < 256 else ("ldr", "=")
    assembly = f"{func} {register}, {sign}{value.content}\n"
    memory[value.content] = register
    return assembly, memory


def stringtoRegister(value: Value, data: dict, register: str = "r0"):
    key = f"LIT{len(data)}"
    data[key] = value.content
    assembly = f"ldr {register}, ={key}\n"
    return assembly, data


def intToRegister(value, register = "r0"):
    content = int(value.content)
    func, sign = ("mov", "#") if content < 256 else ("ldr", "=")
    assembly = f"{func} {register}, {sign}{content}\n"
    return assembly


def ZegNaHelper(arg, memory, data):
    match arg:
        case arg if type(arg) == Variable:
            register = memory[arg.name]
            if register[0].isupper(): # again quite hacky, but very useful
                func = "printlnStr"
            else:
                func = "printlnInteger"
            return f"mov r0, {register}\nbl {func}\n", memory, data
        case arg if type(arg) == Value:
            if '"' in arg.content:
                assembly, data = stringtoRegister(arg, data)
                return assembly+"bl printlnStr\n", memory, data
            assembly = intToRegister(arg)
            return assembly+"bl printlnInteger\n", memory, data


def compileZegNa(toCompile, memory, data):
    assembly, memory, data = ZegNaHelper(toCompile.args[0], memory, data)
    assembly2 = ""
    if rest := toCompile.args[1:]:
        assembly2, memory, data = compileZegNa(
            Expression("zeg_na", len(rest), rest), memory, data)
    return assembly+assembly2, memory, data

# Returns string of assembly needed for this statement

def compileStel(toCompile, memory, data, allRegisters):
    if type(toCompile.args[1]) == Value:
        register = getRegister(allRegisters, memory)
        if type(toCompile.args[1].content) == str:
            memory[toCompile.args[0].name] = register.upper() # this is really shitty, but the capital R denotes a register holding a string
            assembly, data = stringtoRegister(toCompile.args[1], data, register.upper())
            return assembly, memory, data
        else:
            memory[toCompile.args[0].name] = register
            func, sign = ("mov", "#") if toCompile.args[1].content < 256 else (
                "ldr", "=")
            immed = sign + str(toCompile.args[1].content)
            return f"{func} {register}, {immed}\n", memory, data


def compileIf(toCompile, memory, data):
    return            


def compileExpression(toCompile: Expression, memory, data):
    allRegisters = ["r1", "r2", "r3", "r4", "r5", "r6", "r7"]
    funcToAssem = {"produceer": "mul", "stapel": "add", "verklein": "sub"}
    if type(toCompile) == If:
        return compileIf(toCompile, memory, data)

    match toCompile.function:
        case a if a in funcToAssem.keys():
            if type(toCompile.args[1]) == Value:
                memAssem, memory = valueToRegister(
                    toCompile.args[1], memory, allRegisters)
                snd = memory[toCompile.args[1].content]
            else:  # variable
                # for now we assume nothing ends up in memory and everything fits into registers
                memAssem = ""
                snd = memory[toCompile.args[1].name]
            # "memory" will store the location of the data, so a register name or a memory address
            return memAssem + f"{funcToAssem[a]} {memory[toCompile.args[0].name]}, {snd}, {memory[toCompile.args[0].name]}\n", memory, data
        case "stel":
            return compileStel(toCompile, memory, data, allRegisters)
        case "zeg_na":
            return compileZegNa(toCompile, memory, data)
        case _:
            print(":(")
            return


def compileData(data):
    def helper(x, y): return f"{x}: .asciz {y}\n"
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
