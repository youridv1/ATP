import lex as l
import AST as a
import interpreter as i
import sys
import compiler as cmp
import os

sys.setrecursionlimit(20000) # core dumped at 21804

def main(compile: bool, interpet: bool) -> None:
    b = l.lex("youriMain.yo")
    x = a.parse(b)
    if compile:
        cmp.mainCompiler("youriMain", x)
    if interpet:
        i.interpret(x)
    
if __name__ == "__main__":
    compile = "compile" in sys.argv
    interpret = "interpret" in sys.argv
    clean = "clean" in sys.argv

    if clean:
        os.popen('find ./PlatformioProject/src -iname "*.S" -delete')

    os.popen('cp PlatformioProject/lib/print.S PlatformioProject/src/')

    if compile or interpret:
        main(compile, interpret)
    elif not clean:
        print("No option given\nOptions:\n- compile\n- interpret\n- clean\nEnter multiple options if you want to\n")
