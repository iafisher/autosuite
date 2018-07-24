"""Tests for all autosuite functions.

Turns out testing a testing library is pretty confusing!
"""
import inspect
import sys
import unittest
from contextlib import contextmanager
from io import StringIO

from autosuite.autosuite import (
    TestCase, testcase_to_str, format_mod, format_exception_name, EQUAL,
    NOT_EQUAL, EXCEPTION, generate_imports, wrap, gettests, suite, clear
)

from mylib import fib, FibonacciError, FibTestClass

# Patch inspect.stack so that when it is invoked from an instance method of the
# Tester class, it behaves as if it were invoked from the Python shell. The
# autosuite tool uses inspect.stack to ensure the autosuite code isn't
# spuriously invoked for recursive calls, so we have to patch it so that it
# will run in the test suite.
old_inspect_stack = inspect.stack


def new_inspect_stack(*args, **kwargs):
    stack = old_inspect_stack(*args, **kwargs)
    # The top frame of the stack is for the new_inspect_stack function itself.
    stack.pop(0)
    if is_tester_frame(stack[1].frame):
        # Insert a frame that mimics the top level of the Python shell.
        frame = inspect.FrameInfo(frame=None, filename='<stdin>', lineno=1,
            function='<module>', code_context=None, index=None)
        stack.insert(1, frame)
    return stack


def is_tester_frame(frame):
    return isinstance(frame.f_locals.get('self'), Tester)

inspect.stack = new_inspect_stack


def dummy(*args, **kwargs):
    pass


class DummyClass:
    def dummy_method(self):
        pass

class NoRepr:
    pass


class Tester(unittest.TestCase):
    def setUp(self):
        clear()

    def test_testcase_to_str(self):
        case = TestCase(EQUAL, dummy, (1, 2, 3), {'verbose': True}, 42)
        self.assertEqual(testcase_to_str(case),
            'self.assertEqual(test_main.dummy(1, 2, 3, verbose=True), 42)')

        case = TestCase(NOT_EQUAL, dummy, ('abc', True), {}, b'abc')
        self.assertEqual(testcase_to_str(case),
            'self.assertNotEqual(test_main.dummy(\'abc\', True), b\'abc\')')

        case = TestCase(EXCEPTION, fib, (-1,), {}, FibonacciError())
        self.assertEqual(testcase_to_str(case),
            'with self.assertRaises(mylib.FibonacciError):\n    mylib.fib(-1)')

        # Test various combinations of args and kwargs.
        case = TestCase(EQUAL, dummy, (), {}, 0)
        self.assertEqual(testcase_to_str(case),
            'self.assertEqual(test_main.dummy(), 0)')

        case = TestCase(EQUAL, dummy, (), {'whatever': 42}, [6, 7])
        self.assertEqual(testcase_to_str(case),
            'self.assertEqual(test_main.dummy(whatever=42), [6, 7])')

    def test_testcase_to_str_with_method(self):
        case = TestCase(EQUAL, DummyClass.dummy_method, (), {}, '')
        self.assertEqual(testcase_to_str(case),
            'self.assertEqual(test_main.DummyClass.dummy_method(), \'\')')

    def test_testcase_to_str_with_NoRepr(self):
        case = TestCase(EQUAL, dummy, (NoRepr(),), {}, None)
        with self.assertRaises(ValueError):
            testcase_to_str(case)

    def test_format_mod(self):
        self.assertEqual(format_mod('mylib'), 'mylib.')
        self.assertEqual(format_mod('builtins'), '')
        self.assertEqual(format_mod('__main__'), '')

    def test_format_exception_name(self):
        self.assertEqual(format_exception_name(ValueError()), 'ValueError')
        self.assertEqual(format_exception_name(FibonacciError()),
            'mylib.FibonacciError')

    def test_generate_imports(self):
        tests = [
            TestCase(EQUAL, dummy, (1, 2, 3), {}, FibTestClass()),
            TestCase(EXCEPTION, fib, (-1,), {}, FibonacciError()),
        ]
        self.assertEqual(generate_imports(tests),
            'import mylib\nimport test_main')

        tests = [
            TestCase(EQUAL, dummy, (1, 2, 3), {}, FibTestClass()),
        ]
        self.assertEqual(generate_imports(tests),
            'import mylib\nimport test_main')

    def test_empty_suite_prints_nothing(self):
        mock_stdout = StringIO()
        with redirect_io(new_stdout=mock_stdout):
            suite()
        self.assertEqual(mock_stdout.getvalue(), '')

    def test_suite(self):
        tests = gettests()
        tests.extend([
            TestCase(EQUAL, dummy, (1, 2, 3), {}, 42),
            TestCase(EXCEPTION, dummy, (-1,), {}, ValueError()),
        ])
        mock_stdout = StringIO()
        with redirect_io(new_stdout=mock_stdout):
            suite()
        self.assertEqual(mock_stdout.getvalue(), '''\
import unittest

import test_main

class Tester(unittest.TestCase):
    def test_all(self):
        self.assertEqual(test_main.dummy(1, 2, 3), 42)
        with self.assertRaises(ValueError):
            test_main.dummy(-1)

''')

    def test_suite_with_NoRepr(self):
        tests = gettests()
        tests.extend([
            TestCase(EQUAL, dummy, (NoRepr(),), {}, None),
        ])
        mock_stdout = StringIO()
        with redirect_io(new_stdout=mock_stdout):
            suite()
        self.assertEqual(mock_stdout.getvalue(), '')

    def test_wrap(self):
        mock_stdin = StringIO('y\n')
        with redirect_io(new_stdin=mock_stdin):
            wrapped_dummy = wrap(dummy)
            wrapped_dummy()
        tests = gettests()
        self.assertEqual(len(tests), 1)
        self.assertEqual(tests[0], TestCase(EQUAL, dummy, (), {}, None))
        self.assertEqual(mock_stdin.readline(), '')

    def test_wrap_nested(self):
        """Test that an indirect call (i.e., not from the top-level) to a
        wrapped function does not trigger the autosuite prompt.
        """
        mock_stdin = StringIO('y\n')
        mock_stdout = StringIO()
        with redirect_io(mock_stdin, mock_stdout):
            wrapped_dummy = wrap(dummy)
            (lambda: wrapped_dummy())()
            self.assertEqual(len(gettests()), 0)
        # Make sure nothing was read from stdin or written to stdout.
        self.assertEqual(mock_stdin.readline(), 'y\n')
        self.assertEqual(mock_stdout.getvalue(), '')


@contextmanager
def redirect_io(new_stdin=StringIO(), new_stdout=StringIO()):
    """A context manager to redirect stdin and stdout to the given files, and
    restore them when finished.
    """
    stdin_old = sys.stdin
    stdout_old = sys.stdout
    sys.stdin = new_stdin
    sys.stdout = new_stdout
    yield
    sys.stdin = stdin_old
    sys.stdout = stdout_old
