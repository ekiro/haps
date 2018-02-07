import json

import pytest

import chaps
from chaps.scope.instance import InstanceScope


@pytest.fixture
def cfg_file(tmpdir):
    data = {
        'deps': {
            'container': 'chaps.Container'
        }
    }

    f = tmpdir.join('cfg.json')
    f.write(json.dumps(data))
    return str(f.realpath())


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


def test_configure_class_from_file_and_get_object(cfg_file):
    chaps.Container.configure_from_file(cfg_file)
    some_instance = chaps.Container().get_object('container')
    assert isinstance(some_instance, chaps.Container)


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


def test_inject_class_using_class_decorator(some_class):
    chaps.Container.configure({
        'some_class': some_class
    })

    @chaps.inject('some_class')
    class AnotherClass(object):
        pass

    some_instance = AnotherClass()

    assert hasattr(some_instance, 'some_class')
    assert isinstance(some_instance.some_class, some_class)


def test_inject_class_using_class_decorator_with_init(some_class):
    chaps.Container.configure({
        'some_class': some_class
    })

    @chaps.inject('some_class')
    class AnotherClass(object):
        def __init__(self, arg):
            self.arg = arg
            assert hasattr(self, 'some_class')
            assert isinstance(self.some_class, some_class)

    some_instance = AnotherClass('value')

    assert some_instance.arg == 'value'
    assert hasattr(some_instance, 'some_class')
    assert isinstance(some_instance.some_class, some_class)


def test_inject_class_using_class_decorator_with_inherit1(some_class):
    chaps.Container.configure({
        'some_class': some_class
    })

    class BaseClass(object):
        def __init__(self, arg):
            self.arg = arg

    @chaps.inject('some_class')
    class AnotherClass(BaseClass):
        def __init__(self, arg):
            super(AnotherClass, self).__init__(arg)
            assert hasattr(self, 'some_class')
            assert isinstance(self.some_class, some_class)

    some_instance = AnotherClass('value')

    assert some_instance.arg == 'value'
    assert hasattr(some_instance, 'some_class')
    assert isinstance(some_instance.some_class, some_class)


def test_inject_class_using_class_decorator_with_inherit2(some_class):
    chaps.Container.configure({
        'some_class': some_class
    })

    @chaps.inject('some_class')
    class BaseClass(object):
        def __init__(self, arg):
            self.arg = arg
            assert hasattr(self, 'some_class')
            assert isinstance(self.some_class, some_class)

    class AnotherClass(BaseClass):
        def __init__(self, arg):
            super(AnotherClass, self).__init__(arg)
            assert hasattr(self, 'some_class')
            assert isinstance(self.some_class, some_class)

    some_instance = AnotherClass('value')

    assert some_instance.arg == 'value'
    assert hasattr(some_instance, 'some_class')
    assert isinstance(some_instance.some_class, some_class)


def test_inject_class_using_class_decorator_with_inherit3(
        some_class, some_class2):
    chaps.Container.configure({
        'some_class': some_class,
        'some_class2': some_class2
    })

    @chaps.inject('some_class')
    class BaseClass(object):
        def __init__(self, arg):
            self.arg = arg
            assert hasattr(self, 'some_class')
            assert isinstance(self.some_class, some_class)

    @chaps.inject('some_class2')
    class AnotherClass(BaseClass):
        def __init__(self, arg):
            super(AnotherClass, self).__init__(arg)
            assert hasattr(self, 'some_class')
            assert isinstance(self.some_class, some_class)
            assert hasattr(self, 'some_class2')
            assert isinstance(self.some_class2, some_class2)

    some_instance = AnotherClass('value')

    assert some_instance.arg == 'value'
    assert hasattr(some_instance, 'some_class')
    assert isinstance(some_instance.some_class, some_class)
    assert hasattr(some_instance, 'some_class2')
    assert isinstance(some_instance.some_class2, some_class2)


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


def test_inject_class_using_property_instance_annotation(some_class):
    class NewClass(some_class):
        pass

    chaps.Container.configure({
        some_class: NewClass
    })

    class AnotherClass(object):
        injected_instance: some_class = chaps.Inject()

    some_instance = AnotherClass()

    assert hasattr(some_instance, 'injected_instance')
    assert isinstance(some_instance.injected_instance, NewClass)
    instance1 = some_instance.injected_instance
    instance2 = some_instance.injected_instance

    assert instance1 is instance2


def test_inject_class_using_init_annotation(some_class):
    class NewClass(some_class):
        pass

    chaps.Container.configure({
        some_class: NewClass
    })

    class AnotherClass(object):
        @chaps.inject
        def __init__(self, injected_instance: some_class):
            pass

    some_instance = AnotherClass()

    assert hasattr(some_instance, 'injected_instance')
    assert isinstance(some_instance.injected_instance, NewClass)
    instance1 = some_instance.injected_instance
    instance2 = some_instance.injected_instance

    assert instance1 is instance2
