import unittest

from testgen.testgen import Result, _result_to_test
from mylib import fib, FibonacciError


def dummy(*args, **kwargs):
    pass


class MainTest(unittest.TestCase):
    def test_result_to_test(self):
        res = Result(True, False, dummy, (1, 2, 3), {'verbose': True}, 42)
        self.assertEqual(_result_to_test(res),
            '        self.assertEqual(test_main.dummy(1, 2, 3, verbose=True), 42)')

        res = Result(True, True, fib, (-1,), {}, FibonacciError())
        self.assertEqual(_result_to_test(res),
            '        with self.assertRaises(mylib.FibonacciError):\n            mylib.fib(-1)')
