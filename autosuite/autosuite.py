"""autosuite: A small Python utility that facilitates simple, rapid testing
from the Python shell. See the README for more details and API documentation.

Author:  Ian Fisher (iafisher@protonmail.com)
Version: July 2018
"""
import functools
import importlib
import inspect
import sys
import traceback
import unittest
from collections import namedtuple
from contextlib import suppress
from typing import Callable, List


# GLOBAL TEST LIST
# Technically there may be a race condition but it shouldn't matter since this
# module is only intended to be used from the interactive shell.
_tests = []  # type: List[TestCase]


# TestCase: a type to represent a single unit test.
#   typ: one of EQUAL, NOT_EQUAL, or EXCEPTION
#   f: the function to be tested.
#   args, kwargs: the positional and keyword arguments to the functions.
#   result: either the actual result of the function or the exception it
#           raised, depending on the value of the `typ` field.
TestCase = namedtuple('TestCase', ['typ', 'f', 'args', 'kwargs', 'result'])
EQUAL = 'EQ'
NOT_EQUAL = 'NEQ'
EXCEPTION = 'EXC'


##################
# THE PUBLIC API #
##################

def wrap(func: Callable) -> Callable:
    """Return the function wrapped with the autosuite testing code so that
    subsequent invocations will prompt the user to indicate whether it returned
    the expected answer or not. This function may be used as a decorator.
    """

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        global _tests

        # Behave like the original function if not invoked from the top level.
        # This is to prevent recursive functions from prompting the user after
        # each recursive invocation.
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
        response = get_input()
        if response == 'y':
            if case.typ != EXCEPTION:
                case = case._replace(typ=EQUAL)
        elif response == 'n' and case.typ != EXCEPTION:
            case = case._replace(typ=NOT_EQUAL)
        else:
            return

        _tests.append(case)

    return wrapped


def test() -> None:
    """Run the test suite."""
    unittest.main(module='autosuite', exit=False)


def suite(fpath: str = None) -> None:
    """Write the test suite to file as a runnable Python module. If `fpath` is
    not provided, then the test suite is printed to standard output.
    """
    indent = ' ' * 8
    test_body = []
    for case in _tests:
        try:
            casestr = testcase_to_str(case)
        except ValueError:
            continue
        else:
            test_body.append('\n'.join(indent + line
                for line in casestr.splitlines()))
    test_body = '\n'.join(test_body)

    if not test_body:
        return

    imports = generate_imports(_tests)
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
        with open(fpath, 'w') as f:
            f.write(suite_code)


def clear() -> None:
    """Clear the test suite."""
    _tests.clear()


def pop() -> None:
    """Remove the most recent test case from the test suite. Useful if you
    accidentally enter the wrong answer at the autosuite prompt. If the test
    suite is empty, this function does nothing.
    """
    with suppress(IndexError):
        _tests.pop()


def reload(func: Callable) -> Callable:
    """Reload the function from disk. The function may be a function that has
    already been wrapped with autosuite, or a regular function. Regardless, the
    returned function is autosuite-wrapped.

    All the test cases already in the suite that use the function are updated
    to use the new function. Otherwise, the test suite would report spurious
    failures for old versions of the function.
    """
    global _tests

    mod = importlib.reload(sys.modules[func.__module__])
    new_func = getattr(mod, func.__name__)
    for i, case in enumerate(_tests):
        if case.f is func:
            _tests[i] = case._replace(f=new_func)
    return wrap(new_func)


######################
# INTERNAL FUNCTIONS #
######################

class Tester(unittest.TestCase):
    """The TestCase subclass used to run the test suite. It is implicitly
    invoked by test().
    """

    def test_all(self) -> None:
        for case in _tests:
            if case.typ == EQUAL:
                self.assertEqual(case.f(*case.args, **case.kwargs),
                    case.result)
            elif case.typ == NOT_EQUAL:
                self.assertNotEqual(case.f(*case.args, **case.kwargs),
                    case.result)
            elif case.typ == EXCEPTION:
                with self.assertRaises(case.result):
                    case.f(*case.args, **case.kwargs)


def gettests() -> List[TestCase]:
    """Return the test suite as a list of TestCase objects."""
    return _tests


def testcase_to_str(case: TestCase) -> str:
    """Format a test case as a string, for placement inside a test method of a
    unittest.TestCase class. Raises ValueError if the case cannot be
    stringified.
    """
    fcall = format_function_call(case)
    if case.typ == EXCEPTION:
        excname = format_exception_name(case.result)
        return 'with self.assertRaises({}):\n    {}'.format(excname, fcall)
    elif case.typ == EQUAL:
        return 'self.assertEqual({}, {!r})'.format(fcall, case.result)
    else:
        return 'self.assertNotEqual({}, {!r})'.format(fcall, case.result)


def format_function_call(case: TestCase) -> str:
    """Return the function call from which the test case originated, as a
    string. Raises ValueError if any of the arguments cannot be stringified.
    """
    args = []
    for arg in case.args:
        argstr = repr(arg)
        if argstr.startswith('<') and argstr.endswith('>'):
            raise ValueError
        args.append(argstr)
    args = ', '.join(args)
    kwargs = ', '.join('{}={!r}'.format(k, v) for k, v in case.kwargs.items())
    if args and kwargs:
        arglist = args + ', ' + kwargs
    else:
        arglist = args + kwargs
    arglist = '(' + arglist + ')'
    return format_mod(case.f.__module__) + case.f.__qualname__ + arglist


def format_exception_name(exc: Exception) -> str:
    return format_mod(exc.__class__.__module__) + exc.__class__.__qualname__


def format_mod(module) -> str:
    return module + '.' if module not in ('builtins', '__main__') else ''


def generate_imports(tests: List[TestCase]) -> str:
    modules = set()
    for case in tests:
        modules.add(case.f.__module__)
        if case.typ == EXCEPTION:
            modules.add(case.result.__class__.__module__)

        for arg in case.args:
            modules.add(arg.__class__.__module__)

    modules.discard('__main__')
    modules.discard('builtins')
    return '\n'.join('import {}'.format(m) for m in sorted(modules))


def get_input() -> str:
    while True:
        yesno = input('[autosuite] Is this the expected result (yes/no/cancel)? ')
        yesno = yesno.lstrip()
        if yesno and yesno[0] in 'ync':
            return yesno[0]
