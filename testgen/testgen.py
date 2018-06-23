import sys
import traceback
from collections import namedtuple

_tests = []
_running = True
_call_depth = 0

# expected: True if f(*args, **kwargs) should equal result, False otherwise.
# exception: True if f(*args, **kwargs) should result in an exception.
# f: the function to be tested.
# args, kwargs: the positional and keyword arguments to the functions.
# result: either the actual result of the function or the exception it raised, depending on the
#   value of the exception field.
Result = namedtuple('Result', ['expected', 'exception', 'f', 'args', 'kwargs', 'result'])

def register(f):
    def wrapper(*args, **kwargs):
        global _call_depth, _pos_tests, _neg_tests

        if not _running or _call_depth != 0:
            return f(*args, **kwargs)

        _call_depth += 1
        try:
            res = f(*args, **kwargs)
        except Exception as e:
            res = Result(None, True, f, args, kwargs, e)
            traceback.print_exception(type(e), e, sys.exc_info()[2], limit=15)
        else:
            res = Result(None, False, f, args, kwargs, res)
            print(repr(res.result))
        _call_depth -= 1

        while True:
            yesno = input('[testhelper] Is this the expected result (y[es]/n[o]/c[ancel])? ')
            yesno = yesno.lstrip()
            if yesno.startswith('y'):
                res = res._replace(expected=True)
            elif yesno.startswith('n'):
                if res.exception is False:
                    res = res._replace(expected=False)
                else:
                    return
            elif yesno.startswith('c'):
                return

        # NOTE: What happens if the module is reloaded? Presumably the functions won't be.
        _tests.append(res)
    return wrapper

def run():
    global _running

    _running_old = _running
    _running = False
    for f, args, kwargs, res in _pos_tests:
        assert(f(*args, **kwargs) == res)
    for f, args, kwargs, res in _neg_tests:
        assert(f(*args, **kwargs) != res)
    _running = _running_old

def generate(tests=_tests):
    if not tests:
        return ''

    indent = ' ' * 8
    test_body = '\n'.join(indent + _result_to_test(r) for r in tests)
    imports = _generate_imports(tests)
    return '''\
import unittest

{}

class MyTestCase(unittest.TestCase):
    def test_all(self):
{}

'''.format(imports, test_body)

def _result_to_test(res):
    fcall = _format_function_call(res)
    if res.exception:
        excname = _format_exception_name(res.result)
        return 'with self.assertRaises({}):\n    {}'.format(excname, fcall)
    elif res.expected:
        return 'self.assertEqual({}, {!r})'.format(fcall, res.result)
    else:
        return 'self.assertNotEqual({}, {!r})'.format(fcall, res.result)

def _format_function_call(res):
    # TODO: Catch when repr() returns an invalid result (i.e., '<...>')
    args = ', '.join(repr(a) for a in res.args)
    kwargs = ', '.join('{}={!r}'.format(k, v) for k, v in res.kwargs.items())
    if args and kwargs:
        arglist = args + ', ' + kwargs
    else:
        arglist = args + kwargs
    return _format_mod(res.f.__module__) + res.f.__qualname__ + '(' + arglist + ')'

def _format_exception_name(exc):
    return _format_mod(exc.__class__.__module__) + exc.__class__.__qualname__

def _format_mod(module):
    return module + '.' if module not in ('builtins', '__main__') else ''

def _generate_imports(tests):
    modules = set()
    for result in tests:
        modules.add(result.f.__module__)
        if result.exception:
            modules.add(result.result.__class__.__module__)
    modules.discard('__main__')
    modules.discard('builtins')
    return '\n'.join('import {}\n'.format(m) for m in modules)

def on():
    global _running
    _running = True

def off():
    global _running
    _running = False

def toggle():
    global _running
    _running = not _running

def clear():
    global _pos_tests, _neg_tests
    _pos_tests.clear()
    _neg_tests.clear()
