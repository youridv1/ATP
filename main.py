import lex as l
import AST as a
import interpreter as i

def main():
    tokens = l.lex("helloworld.yo")
    ast = a.parse(tokens)
    i.interpret(ast)
    
        
if __name__ == "__main__":
    main()
