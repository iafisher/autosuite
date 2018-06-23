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
        # TODO: Handle functions that raise exceptions?
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
        yesno = input('[testhelper] Is this the expected result (y[es]/n[o]/c[ancel])? ')
        yesno = yesno.lstrip()
        if yesno.startswith('y'):
            res = res._replace(expected=True)
        elif yesno.startswith('n') and res.exception is False:
            res = res._replace(expected=False)
        else:
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

def compile():
    # TODO: Need to generate module imports
    imports = _generate_imports(_tests)
    test_body = '\n'.join(_result_to_test(r) for r in _tests)
    return '''\
import unittest

{}

class MyTestCase(unittest.TestCase):
    def test_all(self):
{}

'''.format(imports, test_body)

def _result_to_test(res):
    args = ', '.join(repr(a) for a in res.args)
    kwargs = ', '.join('{}={!r}'.format(k, v) for k, v in res.kwargs.items())
    if args and kwargs:
        arglist = args + ', ' + kwargs
    else:
        arglist = args + kwargs
    fcall = res.f.__module__ + '.' + res.f.__qualname__ + '(' + arglist + ')'
    indent = ' ' * 8
    if res.exception:
        excname = res.result.__class__.__qualname__
        if res.result.__class__.__module__ not in ('builtins', '__main__'):
            excname = res.result.__class__.__module__ + '.' + excname
        return indent + 'with self.assertRaises({}):\n'.format(excname) + \
            indent + '    ' + fcall
    elif res.expected:
        return indent + 'self.assertEqual({}, {!r})'.format(fcall, res.result)
    else:
        return indent + 'self.assertNotEqual({}, {!r})'.format(fcall, res.result)

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
