import pytest

import chaps


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
    request.addfinalizer(chaps.Container._reset)
