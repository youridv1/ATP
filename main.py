import lex as l
import AST as a
import interpreter as i
import sys

sys.setrecursionlimit(20000) # core dumped at 21804

def main():
    b = l.lex("helloworld.yo")
    for y in b:
        print(y)
    x = a.parse(b)
    for y in x:
        print(y)
    # i.interpret(x)
    
if __name__ == "__main__":
    main()
