from functools import reduce

# I wanted good function composition, similar to haskell dot notation, for readability, so I googled how to
# https://www.geeksforgeeks.org/function-composition-in-python/#:~:text=Function%20composition%20is%20the%20way,second%20function%20and%20so%20on.

def compose(f, g):
    return lambda x: f(g(x))


def composite_function(*func):
    return reduce(compose, func, lambda x: x)
