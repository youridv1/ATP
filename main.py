import lex as l
import AST as a
import interpreter as i
import sys

sys.setrecursionlimit(20000) # core dumped at 21804

def main():
    b = l.lex("helloworld.yo")
    x = a.parse(b)
    i.interpret(x)
    
if __name__ == "__main__":
    main()
