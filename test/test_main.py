import unittest

from testgen.testgen import (
    Result, _result_to_test, _format_mod, generate, _format_exception_name
)

from mylib import fib, FibonacciError


def dummy(*args, **kwargs):
    pass


class Tester(unittest.TestCase):
    def test_result_to_test(self):
        res = Result(True, False, dummy, (1, 2, 3), {'verbose': True}, 42)
        self.assertEqual(_result_to_test(res),
            'self.assertEqual(test_main.dummy(1, 2, 3, verbose=True), 42)')

        res = Result(True, True, fib, (-1,), {}, FibonacciError())
        self.assertEqual(_result_to_test(res),
            'with self.assertRaises(mylib.FibonacciError):\n    mylib.fib(-1)')

    def test_format_mod(self):
        self.assertEqual(_format_mod('mylib'), 'mylib.')
        self.assertEqual(_format_mod('builtins'), '')
        self.assertEqual(_format_mod('__main__'), '')

    def test_format_exception_name(self):
        self.assertEqual(_format_exception_name(ValueError()), 'ValueError')
        self.assertEqual(_format_exception_name(FibonacciError()), 'mylib.FibonacciError')

    def test_generate(self):
        self.assertEqual(generate([]), '')
        tests = [Result(True, False, dummy, (1, 2, 3), {}, 42)]
        self.assertEqual(generate(tests), '''\
import unittest

import test_main


class Tester(unittest.TestCase):
    def test_all(self):
        self.assertEqual(test_main.dummy(1, 2, 3), 42)
''')
