import sys
import traceback
from collections import namedtuple

_tests = []
_running = True
_call_depth = 0

# typ: one of EQUAL, NOT_EQUAL, or EXCEPTION
# f: the function to be tested.
# args, kwargs: the positional and keyword arguments to the functions.
# result: either the actual result of the function or the exception it raised, depending on the
#   value of the exception field.
TestCase = namedtuple('TestCase', ['typ', 'f', 'args', 'kwargs', 'result'])
EQUAL = 'EQ'
NOT_EQUAL = 'NEQ'
EXCEPTION = 'EXC'

class TestSuite:
    def __init__(self):
        self.tests = []
        self.call_depth = 0

    def register(self, f):
        def wrapper(*args, **kwargs):
            if self.call_depth != 0:
                return f(*args, **kwargs)

            self.call_depth += 1
            try:
                res = f(*args, **kwargs)
            except Exception as e:
                case = TestCase(EXCEPTION, f, args, kwargs, e)
                traceback.print_exception(type(e), e, sys.exc_info()[2], limit=15)
            else:
                case = TestCase(None, f, args, kwargs, res)
                print(repr(case.result))
            self.call_depth -= 1

            response = _get_input()
            if response == 'y':
                if case.typ != EXCEPTION:
                    case = case._replace(typ=EQUAL)
            elif response == 'n' and case.typ != EXCEPTION:
                case = case._replace(typ=NOT_EQUAL)
            else:
                return

            # NOTE: What happens if the module is reloaded? Presumably the functions won't be.
            self.tests.append(case)
        return wrapper

    def generate(self):
        if not self.tests:
            return ''

        indent = ' ' * 8
        test_body = '\n'.join(indent + _testcase_to_str(case) for case in self.tests)
        imports = _generate_imports(self.tests)
        return '''\
import unittest

{}

class Tester(unittest.TestCase):
    def test_all(self):
{}
'''.format(imports, test_body)

    def clear(self):
        self.tests.clear()

def _testcase_to_str(case):
    fcall = _format_function_call(case)
    if case.typ == EXCEPTION:
        excname = _format_exception_name(case.result)
        return 'with self.assertRaises({}):\n    {}'.format(excname, fcall)
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
    return '\n'.join('import {}\n'.format(m) for m in modules)

def _get_input():
    while True:
        yesno = input('[testgen] Is this the expected result (y[es]/n[o]/c[ancel])? ')
        yesno = yesno.lstrip()
        if yesno and yesno[0] in 'ync':
            return yesno[0]
