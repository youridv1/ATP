from lex import lex
from AST import Expression, Variable, Value, Loop, Function, Call, If, parse
import sys
import secrets

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
        case Variable(name):
            register = memory[name]
            if register[0].isupper(): # again quite hacky, but very useful
                func = "printlnStr"
            else:
                func = "printlnInteger"
            return f"mov r0, {register}\nbl {func}\n", memory, data
        case Value(content):
            if '"' in content:
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


def loadNameIfComponent(arg, memory, register = "r0"):
  match arg:
    case Variable(name): return f"mov {register}, {memory[name]}\n"
    case Value(_): return intToRegister(arg, register)


def compileComparison(toCompile, memory, data):
  #load lhs
  lhsAssem = loadNameIfComponent(toCompile.LHS, memory)
  #load rhs
  rhsAssem = loadNameIfComponent(toCompile.RHS, memory, "r1")
  return lhsAssem + rhsAssem + "cmp r0, r1\n"


def compileIf(toCompile, memory, data):
    comparison = compileComparison(toCompile, memory, data)
    body, _, _ = compile(toCompile.body, memory, data)
    ifHex = secrets.token_hex(5)
    ifEnd = f"ifEnd_{ifHex}"
    assembly = f"{comparison}bne {ifEnd}\n{body}{ifEnd}:\n"
    return assembly, memory, data


def compileWhileComparison(toCompile, memory, data):
    #load variable
    lhsAssem = loadNameIfComponent(toCompile.Variable, memory)
    #load value
    rhsAssem = loadNameIfComponent(toCompile.Value, memory, "r1")
    return lhsAssem + rhsAssem + "cmp r0, r1\n"


def compileLoop(toCompile, memory, data):
    comparison = compileWhileComparison(toCompile, memory, data)
    body, _, _ = compile(toCompile.body, memory, data)
    whileHex = secrets.token_hex(5)
    whileEnd = f"whileEnd_{whileHex}"
    whileBegin = f"whileBegin_{whileHex}"
    branch = f"beq {whileEnd}\n"
    assembly = f"{whileBegin}:\n{comparison}{branch}{body}b {whileBegin}\n{whileEnd}:\n"
    return assembly, memory, data


def compileDefinition(toCompile, memory, data):
    return


def compileExpression(toCompile: Expression, memory, data):
    allRegisters = ["r4", "r5", "r6", "r7", "r8", "r9", "r10", "r11"]
    funcToAssem = {"produceer": "mul", "stapel": "add", "verklein": "sub"}
    if type(toCompile) == If:
        return compileIf(toCompile, memory, data)
    if type(toCompile) == Loop:
        return compileLoop(toCompile, memory, data)
    if type(toCompile) == Function:
        return compileDefinition(toCompile, memory, data)

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
            return memAssem + f"{funcToAssem[a]} {memory[toCompile.args[0].name]}, {memory[toCompile.args[0].name]}, {snd}\n", memory, data
        case "stel":
            return compileStel(toCompile, memory, data, allRegisters)
        case "zeg_na":
            return compileZegNa(toCompile, memory, data)
        case _:
            print(":(")
            return


def compileData(data):
    bruh = [f"{key}: .asciz {value}\n" for key, value in data.items()]
    return ".data\n\n" + "".join(bruh) + "\n"


def compile(ast: list, memory: dict = {}, data: dict = {}):
    assembly, memory, data = compileExpression(ast[0], memory, data)
    assembly2 = ""
    if rest := ast[1:]:
        assembly2, memory, data = compile(rest, memory, data)
    return assembly+assembly2, memory, data


def mainCompiler(fileName: str, ast: list):
    if not ast:
      ast = parse(lex(f"{fileName}.yo")) 
    compiledCode, memory, data = compile(ast)
    registerList = ", ".join(memory.values())
    push = "push { " + registerList + ", lr }\n"
    pop = "pop { " + registerList + ", pc }\n"
    print(ast)
    print(data)
    dataSegment = compileData(data)
    fileBegin = beginFile(dataSegment)
    with open(f"{fileName}.S", 'w') as f:
        f.write(fileBegin + push + compiledCode + pop)


if __name__ == "__main__":
    fileName = "actuallyhelloworld"
    mainCompiler(fileName)
