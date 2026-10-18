# dummy_functions.py

def add(a, b):
    """Add two numbers."""
    return a + b

def greet(name, greeting="Hello"):
    """Greet a person with a customizable greeting."""
    return f"{greeting}, {name}!"

def multiply(x, y, z):
    """Multiply three numbers."""
    return x * y * z

def complex_operation(x, y, flag=True):
    """Perform a complex operation."""
    if flag:
        return x - y
    else:
        return x + y

def variadic_func(*args, **kwargs):
    """A function with variadic parameters."""
    return args, kwargs
