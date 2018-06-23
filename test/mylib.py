def fib(n):
    if n < 0:
        raise FibonacciError
    elif n <= 2:
        return 1
    else:
        return fib(n-1) + fib(n-2)

class FibonacciError(Exception):
    pass
