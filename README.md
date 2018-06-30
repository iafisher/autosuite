# autosuite
**NOTE**: This project is in beta, and the public API may change without warning.

autosuite is a small Python utility that facilitates simple and rapid testing from the Python shell.
It lets you replay your interactions with testable functions as unit tests so you don't have to
constantly re-type the same expressions as you edit and reload your code. When you're finished, it
will generate a unit-test module with all the recorded interactions, to bootstrap your test suite.

Here's a sample session, with annotations for explanation:

```pycon
>>> import autosuite as au
>>> import fiblib
>>> fib = au.wrap(fiblib.fibonacci)
```

Import the library and wrap the function you wish to test.

```pycon
>>> fib(1)
1
[autosuite] Is this the expected result (y[es]/n[o]/c[ancel])? y
>>> fib(12)
89
[autosuite] Is this the expected result (y[es]/n[o]/c[ancel])? n
```

Invoke the function normally. After it returns, autosuite will ask you whether the result was
correct or not. The 12th Fibonacci number is actually 144, so we answer "no" to the second prompt.
autosuite uses these answers to construct its test suite.

```pycon
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
```

Now that we have a couple of tests, let's run the test suite. As we expect, it tells us that the
answer 89 is incorrect. Let's edit `fiblib.py` to fix the Fibonacci calculator.

```pycon
>>> fib = au.reload(fib)
>>> au.test()
.
----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
>>> print(au.suite())
import unittest

import fiblib

class Tester(unittest.TestCase):
    def test_all(self):
        self.assertEqual(fiblib.fib(1), 1)
        self.assertNotEqual(fiblib.fib(12), 89)
```

Once we've fixed `fiblib.py`, we can reload the test function and run the test suite again. This
time, it passes! If we want to make the autosuite tests the basis of our module's permanent test
suite, we can use the `suite` function to print out the test suite as Python code.
