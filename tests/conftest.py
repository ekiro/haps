import sys

import pytest

import haps
import haps.config

collect_ignore = []
if sys.version_info < (3, 7):
    collect_ignore.append("test_context_scope.py")
    collect_ignore.append("haps/scopes/context.py")


@pytest.fixture(scope='session')
def some_class():
    class SomeClass:
        def fun(self):
            return id(self)

    return SomeClass


@pytest.fixture(scope='session')
def some_class2():
    class SomeClass2:
        def fun(self):
            return id(self)

    return SomeClass2


@pytest.fixture(scope='function', autouse=True)
def reset_containter(request):
    request.addfinalizer(haps.Container._reset)


@pytest.fixture(scope='function', autouse=True)
def reset_config(request):
    request.addfinalizer(
        lambda: setattr(haps.config.Configuration, '_instance', None))
