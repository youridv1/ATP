import lex as l
import AST as a
import interpreter as i

def main():
    i.interpret(a.parse(l.lex("helloworld.yo")))
    
if __name__ == "__main__":
    main()