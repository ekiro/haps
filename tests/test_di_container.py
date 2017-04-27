import pytest

import chaps
from chaps.scope.instance import InstanceScope


def test_configure():
    chaps.Container.configure({})

    assert chaps.Container()


def test_already_configured():
    chaps.Container.configure({})

    with pytest.raises(chaps.AlreadyConfigured):
        chaps.Container.configure({})


def test_not_configured():
    with pytest.raises(chaps.NotConfigured):
        chaps.Container()


def test_configure_class_and_get_object(some_class):
    chaps.Container.configure({
        'some_class': some_class
    })

    some_instance = chaps.Container().get_object('some_class')
    assert isinstance(some_instance, some_class)


def test_inject_class(some_class):
    chaps.Container.configure({
        'some_class': some_class
    })

    class AnotherClass(object):
        @chaps.inject
        def __init__(self, some_class):
            pass

    some_instance = AnotherClass()

    assert hasattr(some_instance, 'some_class')
    assert isinstance(some_instance.some_class, some_class)


def test_not_existing_scope():
    @chaps.scope('custom')
    class CustomScopedClass(object):
        pass

    chaps.Container.configure({
        'custom_scoped_class': CustomScopedClass
    })

    class AnotherClass(object):
        @chaps.inject
        def __init__(self, custom_scoped_class):
            pass

    with pytest.raises(chaps.UnknownScope):
        AnotherClass()


def test_custom_scope():
    @chaps.scope('custom')
    class CustomScopedClass(object):
        pass

    class CustomScope(InstanceScope):
        get_object_called = False

        def get_object(self, class_):
            CustomScope.get_object_called = True
            return super(CustomScope, self).get_object(class_)

    chaps.Container.configure({
        'custom_scoped_class': CustomScopedClass
    })
    chaps.Container().register_scope('custom', CustomScope)

    class AnotherClass(object):
        @chaps.inject
        def __init__(self, custom_scoped_class):
            pass

    some_instance = AnotherClass()
    assert isinstance(some_instance.custom_scoped_class, CustomScopedClass)
    assert CustomScope.get_object_called
