A small Python utility that auto-generates unit tests from an interactive shell session.

## Usage
Fire up a Python shell and import the `testgen` module. Wrap any functions you wish to unit-test
with `testgen.register`:

```python
>>> my_function = testgen.register(my_module.my_function)
```

Then, test and debug as you normally would. Whenever you call the function, you will be prompted to
answer whether the function returned the correct result or not. Your answers to these prompts will
be used to generate the test suite.

Once you're done debugging, then just call `testgen.compile` to generate a complete Python test
module with all the results from your interactive session!

A full sample session:

```python
>>> import mylib, testgen as tg
>>> fibonacci = tg.register(mylib.fibonacci) # The `register` function can also be used as a decorator
>>> fibonacci(12)
144
[testhelper] Is this the expected result (y[es]/n[o]/c[ancel])? y
>>> fibonacci(-1)
Traceback (most recent call last):
  ...
ValueError
[testhelper] Is this the expected result (y[es]/n[o]/c[ancel])? y
>>> print(tg.compile())
import unittest

import mylib

class MyTestCase(unittest.TestCase):
    def test_all(self):
        self.assertEqual(mylib.fibonacci(12), 144)
        with self.assertRaises(ValueError):
            mylib.fibonacci(-1)
```

## API reference
TODO

Alternative names:
- pyshelltest (shelltest is taken)
- testmate
- swandive
