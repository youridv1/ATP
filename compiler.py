import sys
import secrets
from lex import lex
from typing import *
from interpreter import InterpretType, functionalDictAdd
from AST import Expression, Variable, Value, Loop, Function, Call, If, parse, ASTType

sys.setrecursionlimit(20000)  # core dumped at 21804

Register        = str
VariableName    = str
AsmCode         = str
DataSegmentType = Dict[str, str]
CompMemType     = Dict[VariableName, Register]

# beginFile :: DataSegmentType -> str -> str 
def beginFile(dataSegment: DataSegmentType = "", fileName: str = "") -> str:
    '''Formats the top part of an assembly file, inserts the .data segment and the function/file name'''
    return f".cpu cortex-m0\n.align 2\n\n{dataSegment}.text\n.global {fileName}\n\n{fileName}:\n"

# getRegister :: [Register] -> CompMemType -> Register
def getRegister(allRegisters: List[Register], memory: CompMemType) -> Register:
    '''Get the lowest empty register'''
    return [x for x in allRegisters if x.lower() not in memory.values() and x.upper() not in memory.values()][0]


# puts an inline value in r0
# valueToR0 :: Value -> CompMemType -> (AsmCode, CompMemType)
def valueToR0(value: Value, memory: CompMemType) -> Tuple[AsmCode, CompMemType]:
    '''Moves a Value into r0, returns both the necessary assembly code and the new memory'''
    register = "r0"
    func, sign = ("mov", "#") if value.content < 256 else ("ldr", "=")
    assembly = f"{func} {register}, {sign}{value.content}\n"
    return assembly, memory


# stringToRegister :: Value -> DataSegmentType -> Register -> (AsmCode, DataSegmentType)
def stringtoRegister(value: Value, data: DataSegmentType, register: Register = "r0") -> Tuple[AsmCode, DataSegmentType]:
    '''Adds string to data segment and puts pointer in given register
    Returns needed assembly code and new data segment'''
    key = f"LIT{len(data)}"
    assembly = f"ldr {register}, ={key}\n"
    return assembly, functionalDictAdd(data, {key:value.content})


# intToRegister :: Value -> Register -> AsmCode
def intToRegister(value: Value, register: Register="r0") -> AsmCode:
    '''Adds int to given register
    Returns needed assembly code'''
    content = int(value.content)
    func, sign = ("mov", "#") if content < 256 else ("ldr", "=")
    assembly = f"{func} {register}, {sign}{content}\n"
    return assembly


# Haskell doesn't actually support having two types for a parameter I believe. You need to either use a generic type or a type of which both are an implementation
# So I guess I could've used dataclass as a type, but instead I used a |
# ZegNaHelper :: Value | Variable -> CompMemType -> DataSegmentType -> (AsmCode, CompMemType, DataSegmentType)
def ZegNaHelper(arg: Union[Value, Variable], memory: CompMemType, data: DataSegmentType) -> Tuple[AsmCode, CompMemType, DataSegmentType]:
    '''Helper function for printing
    Loads value into r0 and branches to smartPrint
    Returns needed assembly code, new memory and new data segment'''
    match arg:
        case Variable(name):
            register = memory[name]
            return f"mov r0, {register}\nbl smartPrint\n", memory, data
        case Value(content):
            if '"' in content:
                assembly, newdata = stringtoRegister(arg, data)
                return assembly+"bl smartPrint\n", memory, newdata
            assembly = intToRegister(arg)
            return assembly+"bl smartPrint\n", memory, data

# compileZegNa :: Expression -> CompMemType -> DataSegmentType -> (AsmCode, CompMemType, DataSegmentType)
def compileZegNa(toCompile: Expression, memory: CompMemType, data: DataSegmentType) -> Tuple[AsmCode, CompMemType, DataSegmentType]:
    '''Compiles zeg_na Expression to assembly code
    Returns needed assembly code, new memory and new data segment'''
    assembly, memory2, data2 = ZegNaHelper(toCompile.args[0], memory, data)
    if rest := toCompile.args[1:]:
        assembly2, memory3, data3 = compileZegNa(
            Expression("zeg_na", len(rest), rest), memory2, data2)
        return assembly+assembly2, memory3, data3
    return assembly, memory2, data2


# compileStel :: Expression -> CompMemType -> DataSegmentType -> [Register] -> (AsmCode, CompMemType, DataSegmentType)
def compileStel(toCompile: Expression, memory: CompMemType, data: DataSegmentType, allRegisters: List[Register]) -> Tuple[AsmCode, CompMemType, DataSegmentType]:
    '''Compiles stel Expression (assignment) to assembly code
    Returns needed assembly code, new memory and new data segment'''
    register = getRegister(allRegisters, memory)
    newmemory = functionalDictAdd(memory, {toCompile.args[0].name:register})
    if len(toCompile.args) < 3:
        if type(toCompile.args[1]) == Value:
            if type(toCompile.args[1].content) == str:
                assembly, newdata = stringtoRegister(
                    toCompile.args[1], data, register)
                return assembly, newmemory, newdata
            else:
                func, sign = ("mov", "#") if toCompile.args[1].content < 256 else (
                    "ldr", "=")
                immed = sign + str(toCompile.args[1].content)
                return f"{func} {register}, {immed}\n", newmemory, data
        else:
            return f"mov {newmemory[toCompile.args[0].name]}, {newmemory[toCompile.args[1].name]}\n", newmemory, data
    else:
        return f"mov {register}, r{toCompile.args[2].content}\n", newmemory, data

# loadNameIfComponent :: Variable | Value -> CompMemType -> Register -> AsmCode
def loadNameIfComponent(arg: Union[Variable, Value], memory: CompMemType, register: Register="r0") -> AsmCode:
    '''Returns the needed assembly to load the LHS/RHS of an If comparison into r0/r1'''
    match arg:
        case Variable(name): return f"mov {register}, {memory[name]}\n"
        case Value(_): return intToRegister(arg, register)

# compileComparison :: If -> CompMemType -> AsmCode
def compileComparison(toCompile: If, memory: CompMemType) -> AsmCode:
    '''Compiles the comparison in an If expression to assembly code'''
    # load lhs
    lhsAssem = loadNameIfComponent(toCompile.LHS, memory)
    # load rhs
    rhsAssem = loadNameIfComponent(toCompile.RHS, memory, "r1")
    return lhsAssem + rhsAssem + "cmp r0, r1\n"

# compileIf :: If -> CompMemType -> DataSegmentType -> (AsmCode, CompMemType, DataSegmentType)
def compileIf(toCompile: If, memory: CompMemType, data: DataSegmentType) -> Tuple[AsmCode, CompMemType, DataSegmentType]:
    '''Compiles an If statement to assembly code
    Returns the needed assembly code, the new memory and new datasegment type'''
    comparison = compileComparison(toCompile, memory)
    body, _, _ = compile(toCompile.body, memory, data)
    ifHex = secrets.token_hex(5)
    ifEnd = f"ifEnd_{ifHex}"
    assembly = f"{comparison}bne {ifEnd}\n{body}{ifEnd}:\n"
    return assembly

# compileWhileComparison -> Loop -> CompMemType -> AsmCode
def compileWhileComparison(toCompile: Loop, memory: CompMemType) -> AsmCode:
    '''Compiles the comparison in a Loop to assembly code'''
    # load variable
    lhsAssem = loadNameIfComponent(toCompile.LHS, memory)
    # load value
    rhsAssem = loadNameIfComponent(toCompile.RHS, memory, "r1")
    return lhsAssem + rhsAssem + "cmp r0, r1\n"

# compileLoop :: Loop -> CompMemType -> DataSegmentType -> (AsmCode, CompMemType, DataSegmentType)
def compileLoop(toCompile: Loop, memory: CompMemType, data: DataSegmentType) -> Tuple[AsmCode, CompMemType, DataSegmentType]:
    '''Compiles a loop to assembly code 
    Returns the needed assembly code, memory and datasegment'''
    comparison = compileWhileComparison(toCompile, memory)
    body, _, _ = compile(toCompile.body, memory, data)
    whileHex = secrets.token_hex(5)
    whileEnd = f"whileEnd_{whileHex}"
    whileBegin = f"whileBegin_{whileHex}"
    branch = f"beq {whileEnd}\n"
    assembly = f"{whileBegin}:\n{comparison}{branch}{body}b {whileBegin}\n{whileEnd}:\n"
    return assembly

# compileDefinition :: Function -> None
def compileDefinition(toCompile: Function) -> None:
    '''Starts a new compiler to compile a function definition which is put in a seperate assembly file'''
    mainCompiler(toCompile.name, toCompile.body)

def loadArg(arg: Union[Variable, Value], register: Register, memory: CompMemType, data: DataSegmentType, allRegisters: List[Register]) -> Tuple[AsmCode, CompMemType, DataSegmentType]:
    match arg:
        case Value(_):
            if type(arg.content) == int:
                argument, newdata = stringtoRegister(arg, data)
                return argument, memory, newdata
            else:
                argument = intToRegister(arg)
        case Variable(name):
            argument = f"mov {register}, {memory[name]}\n"
    return argument, memory, data

# compileCall :: Call -> CompMemType -> DataSegmentType -> [Register] -> (AsmCode, CompMemType, DataSegmentType)
def compileCall(toCompile: Call, memory: CompMemType, data: DataSegmentType, allRegisters: List[Register]) -> Tuple[AsmCode, CompMemType, DataSegmentType]:
    '''Compiles a function call by loading the parameters into temp registers, branching and moving the result into a new register'''
    if toCompile.argc <= 4:
        registers = ["r0", "r1", "r2", "r3"]
        ArgTuples = list(zip(toCompile.args[:toCompile.argc], registers[:toCompile.argc]))
        arguments = "".join([loadArg(*x, memory, data, allRegisters)[0] for x in ArgTuples])
    else:
        return  
    if toCompile.result:
        register = getRegister(allRegisters, memory)
        newmemory = functionalDictAdd(memory, {toCompile.result:register})
        resultAssembly = f"mov {register}, r0\n"
    else:
        newmemory = {}
        resultAssembly = ""
    callAssembly = f"bl {toCompile.name}\n"
    if newmemory:
        returnMemory = newmemory
    else:
        returnMemory = memory
    return f"{arguments}{callAssembly}{resultAssembly}", returnMemory, data

# compileVerdeel :: Expression -> CompMemType -> AsmCode
def compileVerdeel(toCompile: Expression, memory: CompMemType) -> AsmCode:
    '''compiles a verdeel (division) statement'''
    # load lhs
    lhsAssem = loadNameIfComponent(toCompile.args[0], memory)
    # load rhs
    rhsAssem = loadNameIfComponent(toCompile.args[1], memory, "r1")
    lhsOverWriteAssem = f"mov {memory[toCompile.args[0].name]}, r0\n"
    return lhsAssem + rhsAssem + "bl divide\n" + lhsOverWriteAssem
    

# compileExpression :: InterpretType -> CompMemType -> DataSegmentType -> (AsmCode, CompMemType, DataSegmentType)
def compileExpression(toCompile: InterpretType, memory: CompMemType, data: DataSegmentType) -> Tuple[AsmCode, CompMemType, DataSegmentType]:
    '''Compile any expression that is in the language'''
    allRegisters = ["r4", "r5", "r6", "r7", "r8", "r9", "r10", "r11"]
    funcToAssem = {"produceer": "mul", "stapel": "add", "verklein": "sub"}
    match toCompile:
        case If(_, _, _):
            return compileIf(toCompile, memory, data), memory, data
        case Loop(_, _, _):
            return compileLoop(toCompile, memory, data), memory, data
        case Function(_, _):
            compileDefinition(toCompile)
            return f"@definition of {toCompile.name} was performed\n", memory, data
        case Call(_, _, _, _):
            return compileCall(toCompile, memory, data, allRegisters)
        case Expression(a, _, _) if a in funcToAssem.keys():
            if type(toCompile.args[1]) == Value:
                memAssem, memory = valueToR0(
                    toCompile.args[1], memory)
                snd = "r0"
            else:
                memAssem = ""
                snd = memory[toCompile.args[1].name]
            # "memory" will store the location of the data, so a register name or a memory address
            return memAssem + f"{funcToAssem[a]} {memory[toCompile.args[0].name]}, {memory[toCompile.args[0].name]}, {snd}\n", memory, data
        case Expression("stel", _, _):
            return compileStel(toCompile, memory, data, allRegisters)
        case Expression("zeg_na",_ ,_):
            return compileZegNa(toCompile, memory, data)
        case Expression("verdeel", _,_):
            return compileVerdeel(toCompile, memory), memory, data
        case _:
            print(":(")
            return

# compileDaa :: DataSegmentType -> str
def compileData(data: DataSegmentType) -> str:
    '''Compile/Format the datasegment to be pasted into the assembly file'''
    dataSegment = [f"{key}: .asciz {value}\n" for key, value in data.items()]
    if dataSegment:
        return ".data\n\n" + "".join(dataSegment) + "\n"
    return ""

# compile :: ASTTYPE -> CompMemType -> DataSegmentType -> (AsmCode, CompMemType, DataSegmentType)
def compile(ast: ASTType, memory: CompMemType = {}, data: DataSegmentType = {}) -> Tuple[AsmCode, CompMemType, DataSegmentType]:
    '''Compiles an AST to assembly code, memory and data segment'''
    if not memory:
        memory = {}
    assembly, memory2, data2 = compileExpression(ast[0], memory, data)
    if rest := ast[1:]:
        assembly2, memory3, data3 = compile(rest, memory2, data2)
        return assembly+assembly2, memory3, data3
    return assembly, memory2, data2

# mainCompiler -> str -> ASTType -> None
def mainCompiler(fileName: str, ast: ASTType = []) -> None:
    '''Main compiler routine
    Formats the file and calls all necessary functions
    Keeps track of data segment and which registers to push and pop'''
    if not ast:
        # only used for youriMain.yo
        ast = parse(lex(f"{fileName}.yo"))
    compiledCode, memory, data = compile(ast, {}, {})

    entryList = memory.keys()
    if "result" in entryList:
        result = memory["result"]
        returnStatement = f"mov r0, {result}\n"
    else:
        returnStatement = ""

    registerList = memory.values()
    exceptedRegisters = ["r0", "r1", "r2", "r3"]
    popPushRegisters = sorted([x for x in registerList if x not in exceptedRegisters])
    popPushRegisterString = ", ".join(popPushRegisters)
    if popPushRegisterString:
        push = "push { " + popPushRegisterString + ", lr }\n"
        pop = "pop { " + popPushRegisterString + ", pc }\n"
    else:
        push = "push { lr }\n"
        pop = "pop { pc }\n"

    dataSegment = compileData(data)
    fileBegin = beginFile(dataSegment, fileName)
    with open(f"./PlatformioProject/src/{fileName}.S", 'w') as f:
        f.write(fileBegin + push + compiledCode + returnStatement + pop)


if __name__ == "__main__":
    fileName = "youriMain"
    mainCompiler(fileName)
