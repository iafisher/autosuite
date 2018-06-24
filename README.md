# autosuite
autosuite is a small Python utility that automatically generates unit tests from interactive shell
sessions. All you have to do is hook in the autosuite library, debug your programs as you normally
would in the Python shell, and when you're finished autosuite will generate a working unit-test
module for you based on your interactions!

Here's how to use it:

```python
>>> import mylib, autosuite
>>> ts = autosuite.TestSuite()
>>> fibonacci = ts.register(mylib.fibonacci)
>>> fibonacci(12)
144
[autosuite] Is this the expected result (y[es]/n[o]/c[ancel])? y
>>> fibonacci(-1)
Traceback (most recent call last):
  ...
ValueError
[autosuite] Is this the expected result (y[es]/n[o]/c[ancel])? y
>>> print(ts.generate())
import unittest

import mylib

class Tester(unittest.TestCase):
    def test_all(self):
        self.assertEqual(mylib.fibonacci(12), 144)
        with self.assertRaises(ValueError):
            mylib.fibonacci(-1)
```

You can also use the `register` function as a decorator:

```python
import autosuite

ts = autosuite.TestSuite()

@ts.register
def fibonacci(n):
   ...
```

## Installation
Clone the repository locally:

```
$ git clone https://github.com/iafisher/autosuite.git
```

Install:
```
$ python3 setup.py install
```

## API reference
TODO

## Limitations
autosuite makes use of Python's introspection capabilities, but not everything can be accomplished
perfectly. autosuite's goal is get your unit tests up and running with minimal effort, but in some
more complex cases the generated test module might require small modifications.

Here are the known limitations:

- All arguments passed to functions that you are testing must be recoverable from their `repr`
  string. That is, `o == eval(repr(o))` must be true. This property holds for almost all built-in
  types [1] and is explicitly recommended for implementations of `repr` by the
  [Python Language Reference](https://docs.python.org/3.5/reference/datamodel.html#object.__repr__),
  but for some types it is not possible.

[1] Memoryviews, module objects, function objects, class objects, and perhaps some other uncommon
    types are not reconstructable from their `repr`s.
