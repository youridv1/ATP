import lex as l
import AST as a
import interpreter as i
import sys
import compiler as cmp

sys.setrecursionlimit(20000) # core dumped at 21804

def main(compiler: bool, interpeter: bool) -> None:
    b = l.lex("youriMain.yo")
    x = a.parse(b)
    if compiler:
        cmp.mainCompiler("youriMain", x)
    if interpeter:
        i.interpret(x)
    
if __name__ == "__main__":
    compiler = "compile" in sys.argv
    interpreter = "interpret" in sys.argv
    if compiler or interpreter:
        main(compiler, interpreter)
    else:
        print("No option given\nOptions:\n- compile\n- interpret\nEnter both options if you want to do both\n")
