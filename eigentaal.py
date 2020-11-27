import lex as l

def main():
    tokens = l.lex("helloworld.yo")
    for token in tokens:
        print(token)
        
if __name__ == "__main__":
    main()
