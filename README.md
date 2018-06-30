# autosuite
**NOTE**: This project is in beta, and the public API may change without warning.

autosuite is a small Python utility that facilitates simple and rapid testing from the Python shell.
It lets you replay your interactions with testable functions as unit tests so you don't have to
constantly re-type the same expressions as you edit and reload your code. When you're finished, it
will generate a unit-test module with all the recorded interactions, to bootstrap your test suite.

Here's a sample session:

```pycon
>>> import autosuite as au
>>> import fiblib
>>> fib = au.wrap(fiblib.fibonacci)
>>> fib(1)
1
[autosuite] Is this the expected result (y[es]/n[o]/c[ancel])? y
>>> fib(12)
89
[autosuite] Is this the expected result (y[es]/n[o]/c[ancel])? n
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
>>> # Let's edit the fiblib.py module to fix the mistake.
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
