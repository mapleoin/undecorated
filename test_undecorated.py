# -*- coding: utf-8 -*-
# Copyright 2016 Ionuț Arțăriși <ionut@artarisi.eu>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from functools import wraps

from undecorated import undecorated


def decorate(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # 'd' is a marker to make it easy to assert that the wrapper was
        # run
        return f(*args, **kwargs) + ('d', )
    return wrapper


def decorate_with_params(*d_args, **d_kwargs):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs) + d_args + tuple(d_kwargs.items())
        return wrapper
    return decorator


def decorate_with_callback(call_back, *d_args, **d_kwargs):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs) + call_back(*d_args, **d_kwargs)
        return wrapper
    return decorator


def f(a, b=2):
    return ('original', )


def test_simple_undecorate():
    decorated = decorate(f)

    assert decorated(None) == ('original', 'd')
    assert decorated(None, 3) == ('original', 'd')
    assert undecorated(decorated) is f
    assert undecorated(decorated)(None) == ('original', )


def test_with_params():
    decorated = decorate_with_params('a', kwarg1='b')(f)

    assert decorated(1, 2) == ('original', 'a', ('kwarg1', 'b'))
    assert undecorated(decorated) is f
    assert undecorated(decorated)(None) == ('original', )


def test_with_callback():
    decorated = decorate_with_callback(lambda: ('b',))(f)

    assert decorated(1, 2) == ('original', 'b')
    assert undecorated(decorated) is f
    assert undecorated(decorated)(None) == ('original', )


def test_thrice_decorated():
    decorated = decorate_with_params(2)(
        decorate(
            decorate_with_params(1)(f)))

    assert decorated(0, 0) == ('original', 1, 'd', 2)
    assert undecorated(decorated) is f
    assert undecorated(decorated)(None) == ('original', )


def test_params_to_decorator_are_functions():
    def foo():
        pass

    decorated = decorate_with_params(foo)(
        decorate_with_params(foo, foo)(f))

    assert decorated(0) == ('original', foo, foo, foo)
    assert undecorated(decorated) is f
    assert undecorated(decorated)(None) == ('original', )


def test_decorator_without_wraps():
    def lame_decorator(f):
        def decorator(*args, **kwargs):
            f(*args, **kwargs)
        return decorator

    decorated = lame_decorator(f)

    assert undecorated(decorated) is f
    assert undecorated(decorated)(None) == ('original', )


def test_infinite_recursion():
    def recursive_decorator(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            decorator.foo()
            return f(*args, **kwargs)

        decorator.foo = lambda: None

        return decorator

    decorated = recursive_decorator(f)

    assert decorated(None) == ('original', )
    assert undecorated(decorated) is f
    assert undecorated(decorated)(None) == ('original', )


def test_simple_method():
    class A(object):
        def foo(self, a, b):
            return a, b

    decorated = decorate_with_params('dp')(decorate(A.foo))

    assert decorated(A(), 1, 2) == (1, 2, 'd', 'dp')
    assert undecorated(decorated) == A.foo
    assert undecorated(decorated)(A(), 1, 2) == (1, 2)


def test_not_decorated():
    def foo(self, a, b):
        return a, b

    assert undecorated(f) is f


def test_class_decorator():
    def decorate(cls):
        def dec():
            ins = cls()
            ins.decorated = True
            return ins
        return dec

    class A(object):
        decorated = False

    decorated = decorate(A)

    assert decorated().decorated is True
    assert undecorated(decorated) is A
    assert undecorated(decorated)().decorated is False
