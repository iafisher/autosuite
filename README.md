# autosuite
**NOTE**: This project is in beta, and the public API may change without
warning.

autosuite is a small Python utility that facilitates simple, rapid testing from
the Python shell. It lets you replay your interactions with testable functions
as unit tests so you don't have to constantly re-type the same test expressions
as you edit and reload your code. When you're finished, it will help you
bootstrap your unit tests by generating a Python `unittest` module with all the
interactions it recorded.

Here's a sample session:

```pycon
# Import the library and wrap the function you wish to test.
>>> import autosuite as au
>>> import fiblib
>>> fib = au.wrap(fiblib.fibonacci)

# Invoke the function normally. After it returns, autosuite will ask you whether
# the result was correct or not. The 12th Fibonacci number is actually 144, so
# we answer "no" to the second prompt. autosuite uses these answers to construct
# its test suite.
>>> fib(1)
1
[autosuite] Is this the expected result (yes/no/cancel)? y
>>> fib(12)
89
[autosuite] Is this the expected result (yes/no/cancel)? n

# Now that we have a couple of tests, let's run the test suite. As we expect, it
# tells us that the answer 89 is incorrect. Let's edit `fiblib.py` to fix the
# Fibonacci calculator.
>>> au.test()
F
======================================================================
FAIL: test_all (autosuite.autosuite.Tester)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/.../autosuite/autosuite.py", line 69, in test_all
    self.assertNotEqual(case.f(*case.args, **case.kwargs), case.result)
AssertionError: 89 == 89

----------------------------------------------------------------------
Ran 1 test in 0.001s

FAILED (failures=1)

# Once we've fixed `fiblib.py`, we can reload the test function and run the test
# suite again:
>>> fib = au.reload(fib)
>>> au.test()
.
----------------------------------------------------------------------
Ran 1 test in 0.001s

OK

# This time, it passes! If we want to make the autosuite tests the basis of our
# module's permanent test suite, we can use the `suite` function to print out the
# test suite as Python code.
>>> au.suite()
import unittest

import fiblib

class Tester(unittest.TestCase):
    def test_all(self):
        self.assertEqual(fiblib.fib(1), 1)
        self.assertNotEqual(fiblib.fib(12), 89)
```

## API reference
`clear() -> None`: Clear the test suite.

`pop() -> None`: Remove the most recent test case from the test suite. Useful
if you accidentally enter the wrong answer at the autosuite prompt. If the
test suite is empty, this function does nothing.

`reload(func: Callable) -> Callable`: Reload the function from disk. The
function may be a function that has already been wrapped with autosuite, or a
regular function. Regardless, the returned function is autosuite-wrapped.

All the test cases already in the suite that use the function are updated to
use the new function. Otherwise, the test suite would report spurious failures
for old versions of the function.

`suite(fpath: str = None) -> None`: Write the test suite to file as a runnable
Python module. If `fpath` is not provided, then the test suite is printed to
standard output.

`test() -> None`: Run the test suite.

`wrap(func: Callable) -> Callable`: Return the function wrapped with the
autosuite testing code so that subsequent invocations will prompt the user to
indicate whether it returned the expected answer or not. This function may be
used as a decorator.
