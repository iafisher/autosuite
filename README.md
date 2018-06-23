A small Python utility that auto-generates unit tests from an interactive shell session.

## Usage
Fire up a Python shell, import the `testgen` module, and initialize a `TestSuite` object. Wrap any
functions you wish to unit-test with `TestSuite.register`:

```python
>>> tg = testgen.TestSuite()
>>> my_function = tg.register(my_module.my_function)
```

Then, test and debug as you normally would. Whenever you call the function, you will be prompted to
answer whether the function returned the correct result or not. Your answers to these prompts will
be used to generate the test suite.

Once you're done debugging, then just call `testgen.compile` to generate a complete Python test
module with all the results from your interactive session!

A full sample session:

```python
>>> import mylib, testgen
>>> tg = testgen.TestSuite()
>>> fibonacci = tg.register(mylib.fibonacci) # The `register` function can also be used as a decorator
>>> fibonacci(12)
144
[testgen] Is this the expected result (y[es]/n[o]/c[ancel])? y
>>> fibonacci(-1)
Traceback (most recent call last):
  ...
ValueError
[testgen] Is this the expected result (y[es]/n[o]/c[ancel])? y
>>> print(tg.generate())
import unittest

import mylib

class Tester(unittest.TestCase):
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

## Limitations
testgen makes use of Python's introspection capabilities, but not everything can be accomplished
perfectly. testgen's goal is get your unit tests up and running with minimal effort, but in some
more complex cases the generated test module might require small modifications.

Here are the known limitations:

- All arguments passed to functions that you are testing must be recoverable from their `repr`
  string. That is, `o == eval(repr(o))` must be true. This property holds for almost all built-in
  types [1] and is explicitly recommended for implementations of `repr` by the
  [Python Language Reference](https://docs.python.org/3.5/reference/datamodel.html#object.__repr__),
  but for some types it is not possible.

[1] Memoryviews, module objects, function objects, class objects, and perhaps some other uncommon
    types are not reconstructable from their `repr`s.
