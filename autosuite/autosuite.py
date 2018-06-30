import functools
import importlib
import inspect
import sys
import traceback
import unittest
from collections import defaultdict, namedtuple
from contextlib import suppress


# GLOBAL TEST LIST
_tests = []


# typ: one of EQUAL, NOT_EQUAL, or EXCEPTION
# f: the function to be tested.
# args, kwargs: the positional and keyword arguments to the functions.
# result: either the actual result of the function or the exception it raised, depending on the
#   value of the exception field.
TestCase = namedtuple('TestCase', ['typ', 'f', 'args', 'kwargs', 'result'])
EQUAL = 'EQ'
NOT_EQUAL = 'NEQ'
EXCEPTION = 'EXC'


def wrap(func):
    """Wrap the function with the autosuite testing code."""

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        global _tests

        # Behave like the original function if not invoked from the top level.
        if inspect.stack()[1].function != '<module>':
            return func(*args, **kwargs)

        # TODO: Should I make a deepcopy of the args and kwargs?
        try:
            res = func(*args, **kwargs)
        except Exception as e:
            case = TestCase(EXCEPTION, func, args, kwargs, e)
            traceback.print_exception(type(e), e, sys.exc_info()[2], limit=15)
        else:
            case = TestCase(None, func, args, kwargs, res)
            print(repr(case.result))

        # TODO: Don't prompt if the test case is already in the suite.
        response = _get_input()
        if response == 'y':
            if case.typ != EXCEPTION:
                case = case._replace(typ=EQUAL)
        elif response == 'n' and case.typ != EXCEPTION:
            case = case._replace(typ=NOT_EQUAL)
        else:
            return

        _tests.append(case)

    return wrapped


def test():
    """Run the collected tests using Python's unittest library."""
    unittest.main(module='autosuite', exit=False)

class Tester(unittest.TestCase):
    """The TestCase subclass used to run the test suite."""

    def test_all(self):
        for case in _tests:
            if case.typ == EQUAL:
                self.assertEqual(case.f(*case.args, **case.kwargs), case.result)
            elif case.typ == NOT_EQUAL:
                self.assertNotEqual(case.f(*case.args, **case.kwargs), case.result)
            elif case.typ == EXCEPTION:
                with self.assertRaises(case.result):
                    case.f(*case.args, **case.kwargs)


def gettests():
    """Return the test suite as a list of TestCase objects. This method is for testing purposes and
    should not generally be used directly.
    """
    return _tests


def suite(fpath=None):
    """Write the test suite to file as Python code using the unittest library. If fpath is None (the
    default), then the test suite is printed to standard output.
    """
    if not _tests:
        return ''

    indent = ' ' * 8
    test_body = '\n'.join(indent + _testcase_to_str(case) for case in _tests)
    imports = _generate_imports(_tests)
    suite_code = '''\
import unittest

{}

class Tester(unittest.TestCase):
    def test_all(self):
{}
'''.format(imports, test_body)

    if fpath is None:
        print(suite_code)
    else:
        with open(fpath, 'w'):
            fpath.write(suite_code)


def clear():
    """Clear all tests from the suite."""
    _tests.clear()


def pop():
    """Remove the most recent test case from the test suite. Useful if you accidentally enter the
    wrong answer at the autosuite prompt.

    If the test suite is empty, this function does nothing.
    """
    with suppress(IndexError):
        _tests.pop()


def reload(func):
    """Reload the function from disk. The function may be a function that has already been wrapped
    with autosuite, or a regular function. Regardless, the returned function is autosuite-wrapped.

    All the test cases already in the suite that use the function are updated to use the new
    function. Otherwise, the test suite would report spurious failures for old versions of the
    function.
    """
    global _tests

    mod = importlib.reload(sys.modules[func.__module__])
    new_func = getattr(mod, func.__name__)
    for i, case in enumerate(_tests):
        if case.f is func:
            _tests[i] = case._replace(f=new_func)
    return wrap(new_func)


def _testcase_to_str(case):
    # TODO: Fail gracefully for args and kwargs that do not have valid reprs.
    fcall = _format_function_call(case)
    if case.typ == EXCEPTION:
        excname = _format_exception_name(case.result)
        # TODO: Clean this up by removing the indent-insertion in the second line and putting it
        # elsewhere.
        return 'with self.assertRaises({}):\n            {}'.format(excname, fcall)
    elif case.typ == EQUAL:
        return 'self.assertEqual({}, {!r})'.format(fcall, case.result)
    else:
        return 'self.assertNotEqual({}, {!r})'.format(fcall, case.result)

def _format_function_call(case):
    # TODO: Catch when repr() returns an invalid result (i.e., '<...>')
    args = ', '.join(repr(a) for a in case.args)
    kwargs = ', '.join('{}={!r}'.format(k, v) for k, v in case.kwargs.items())
    if args and kwargs:
        arglist = args + ', ' + kwargs
    else:
        arglist = args + kwargs
    return _format_mod(case.f.__module__) + case.f.__qualname__ + '(' + arglist + ')'

def _format_exception_name(exc):
    return _format_mod(exc.__class__.__module__) + exc.__class__.__qualname__

def _format_mod(module):
    return module + '.' if module not in ('builtins', '__main__') else ''

def _generate_imports(tests):
    modules = set()
    for case in tests:
        modules.add(case.f.__module__)
        if case.typ == EXCEPTION:
            modules.add(case.result.__class__.__module__)
    modules.discard('__main__')
    modules.discard('builtins')
    return '\n'.join('import {}'.format(m) for m in sorted(modules))

def _get_input():
    while True:
        yesno = input('[autosuite] Is this the expected result (y[es]/n[o]/c[ancel])? ')
        yesno = yesno.lstrip()
        if yesno and yesno[0] in 'ync':
            return yesno[0]
