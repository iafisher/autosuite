import sys
import unittest
from contextlib import contextmanager
from io import StringIO

from autosuite.autosuite import (
    TestSuite, TestCase, _testcase_to_str, _format_mod, _format_exception_name, EQUAL, NOT_EQUAL,
    EXCEPTION, _generate_imports, _format_function_call
)

from mylib import fib, FibonacciError


def dummy(*args, **kwargs):
    pass

class DummyClass:
    def dummy_method(self):
        pass


class Tester(unittest.TestCase):
    def test_testcase_to_str(self):
        case = TestCase(EQUAL, dummy, (1, 2, 3), {'verbose': True}, 42)
        self.assertEqual(_testcase_to_str(case),
            'self.assertEqual(test_main.dummy(1, 2, 3, verbose=True), 42)')

        case = TestCase(NOT_EQUAL, dummy, ('abc', True), {}, b'abc')
        self.assertEqual(_testcase_to_str(case),
            'self.assertNotEqual(test_main.dummy(\'abc\', True), b\'abc\')')

        case = TestCase(EXCEPTION, fib, (-1,), {}, FibonacciError())
        self.assertEqual(_testcase_to_str(case),
            'with self.assertRaises(mylib.FibonacciError):\n            mylib.fib(-1)')

        # Test various combinations of args and kwargs.
        case = TestCase(EQUAL, dummy, (), {}, 0)
        self.assertEqual(_testcase_to_str(case), 'self.assertEqual(test_main.dummy(), 0)')

        case = TestCase(EQUAL, dummy, (), {'whatever': 42}, [6, 7])
        self.assertEqual(_testcase_to_str(case),
            'self.assertEqual(test_main.dummy(whatever=42), [6, 7])')

    def test_testcase_to_str_with_method(self):
        case = TestCase(EQUAL, DummyClass.dummy_method, (), {}, '')
        self.assertEqual(_testcase_to_str(case),
            'self.assertEqual(test_main.DummyClass.dummy_method(), \'\')')

    def test_format_mod(self):
        self.assertEqual(_format_mod('mylib'), 'mylib.')
        self.assertEqual(_format_mod('builtins'), '')
        self.assertEqual(_format_mod('__main__'), '')

    def test_format_exception_name(self):
        self.assertEqual(_format_exception_name(ValueError()), 'ValueError')
        self.assertEqual(_format_exception_name(FibonacciError()), 'mylib.FibonacciError')

    def test_generate_imports(self):
        tests = [
            TestCase(EQUAL, dummy, (1, 2, 3), {}, 42),
            TestCase(EXCEPTION, fib, (-1,), {}, FibonacciError()),
        ]
        self.assertEqual(_generate_imports(tests), 'import mylib\nimport test_main')

    def test_generate(self):
        tg = TestSuite()
        self.assertEqual(tg.generate(), '')
        tg.tests = [
            TestCase(EQUAL, dummy, (1, 2, 3), {}, 42),
            TestCase(EXCEPTION, dummy, (-1,), {}, ValueError()),
        ]
        self.assertEqual(tg.generate(), '''\
import unittest

import test_main

class Tester(unittest.TestCase):
    def test_all(self):
        self.assertEqual(test_main.dummy(1, 2, 3), 42)
        with self.assertRaises(ValueError):
            test_main.dummy(-1)
''')

        tg.clear()
        self.assertEqual(tg.generate(), '')

    def test_record(self):
        ts = TestSuite()
        mock_stdin = StringIO('y\n')
        with redirect_io(mock_stdin):
            wrapped_dummy = ts.record(dummy)
            wrapped_dummy()
            self.assertEqual(len(ts.tests), 1)
            self.assertEqual(ts.tests[0], TestCase(EQUAL, dummy, (), {}, None))
        self.assertEqual(mock_stdin.readline(), '')

    def test_record_nested(self):
        """Test that an indirect call (i.e., not from the top-level) to a recorded function does not
        trigger the autosuite prompt.
        """
        ts = TestSuite()
        mock_stdin = StringIO('y\n')
        mock_stdout = StringIO()
        with redirect_io(mock_stdin, mock_stdout):
            wrapped_dummy = ts.record(dummy)
            (lambda: wrapped_dummy())()
            self.assertEqual(len(ts.tests), 0)
        # Make sure nothing was read from stdin or written to stdout.
        self.assertEqual(mock_stdin.readline(), 'y\n')
        self.assertEqual(mock_stdout.getvalue(), '')


@contextmanager
def redirect_io(new_stdin, new_stdout=StringIO()):
    """A context manager to redirect stdin and stdout to the given files, and restore them when
    finished.
    """
    stdin_old = sys.stdin
    stdout_old = sys.stdout
    sys.stdin = new_stdin
    sys.stdout = new_stdout
    yield
    sys.stdin = stdin_old
    sys.stdout = stdout_old
