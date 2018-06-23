import unittest

from testgen.testgen import (
    TestCase, _testcase_to_str, _format_mod, generate, _format_exception_name, EQUAL, NOT_EQUAL,
    EXCEPTION
)

from mylib import fib, FibonacciError


def dummy(*args, **kwargs):
    pass


class Tester(unittest.TestCase):
    def test_testcase_to_str(self):
        res = TestCase(EQUAL, dummy, (1, 2, 3), {'verbose': True}, 42)
        self.assertEqual(_testcase_to_str(res),
            'self.assertEqual(test_main.dummy(1, 2, 3, verbose=True), 42)')

        res = TestCase(EXCEPTION, fib, (-1,), {}, FibonacciError())
        self.assertEqual(_testcase_to_str(res),
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
        tests = [TestCase(EQUAL, dummy, (1, 2, 3), {}, 42)]
        self.assertEqual(generate(tests), '''\
import unittest

import test_main


class Tester(unittest.TestCase):
    def test_all(self):
        self.assertEqual(test_main.dummy(1, 2, 3), 42)
''')
