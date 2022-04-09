import sys

# error :: str -> None
def error(a: str) -> None:
    '''Prints string a and stops the current program'''
    print(a)
    sys.exit()