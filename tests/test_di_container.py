import json

import pytest

import chaps
from chaps import exceptions
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
    chaps.Container.configure([])

    assert chaps.Container()


def test_already_configured():
    chaps.Container.configure([])

    with pytest.raises(exceptions.AlreadyConfigured):
        chaps.Container.configure([])


def test_not_configured():
    with pytest.raises(exceptions.NotConfigured):
        chaps.Container()


def test_configure_class_and_get_object(some_class):
    chaps.Container.configure([
        chaps.Egg(some_class, some_class, None, some_class)
    ])

    some_instance = chaps.Container().get_object(some_class)
    assert isinstance(some_instance, some_class)


def test_inject_class(some_class):
    chaps.Container.configure([
        chaps.Egg(some_class, some_class, None, some_class)
    ])

    class AnotherClass(object):
        @chaps.inject
        def __init__(self, some_class_instance: some_class):
            self.some_class_instance = some_class_instance

    some_instance = AnotherClass()

    assert isinstance(some_instance.some_class_instance, some_class)


def test_not_existing_scope():
    @chaps.scope('custom')
    class CustomScopedCls(object):
        pass

    chaps.Container.configure([
        chaps.Egg(CustomScopedCls, CustomScopedCls, None, CustomScopedCls)
    ])

    class AnotherClass(object):
        @chaps.inject
        def __init__(self, csc: CustomScopedCls):
            pass

    with pytest.raises(exceptions.UnknownScope):
        AnotherClass()


def test_custom_scope():
    @chaps.scope('custom')
    class CustomScopedCls(object):
        pass

    class CustomScope(InstanceScope):
        get_object_called = False

        def get_object(self, egg_):
            CustomScope.get_object_called = True
            return super(CustomScope, self).get_object(egg_)

    chaps.Container.configure([
        chaps.Egg(CustomScopedCls, CustomScopedCls, None, CustomScopedCls)
    ])
    chaps.Container().register_scope('custom', CustomScope)

    class AnotherClass(object):
        @chaps.inject
        def __init__(self, csc: CustomScopedCls):
            self.csc = csc

    some_instance = AnotherClass()
    assert isinstance(some_instance.csc, CustomScopedCls)
    assert CustomScope.get_object_called


def test_inject_class_using_property_instance_annotation(some_class):
    class NewClass(some_class):
        pass

    chaps.Container.configure([
        chaps.Egg(some_class, some_class, None, NewClass)
    ])

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

    chaps.Container.configure([
        chaps.Egg(some_class, some_class, None, NewClass)
    ])

    class AnotherClass(object):
        @chaps.inject
        def __init__(self, injected_instance: some_class):
            self.injected_instance = injected_instance

    some_instance = AnotherClass()

    assert hasattr(some_instance, 'injected_instance')
    assert isinstance(some_instance.injected_instance, NewClass)
    instance1 = some_instance.injected_instance
    instance2 = some_instance.injected_instance

    assert instance1 is instance2


def test_named_configuration_property_injection(some_class):
    class NewClass(some_class):
        pass

    class NewClass2(some_class):
        pass

    chaps.Container.configure([
        chaps.Egg(some_class, some_class, None, NewClass),
        chaps.Egg(some_class, some_class, 'extra', NewClass2)
    ])

    class AnotherClass(object):
        some_instance: some_class = chaps.Inject()
        some_extra_instance: some_class = chaps.Inject('extra')

    some_instance = AnotherClass()

    assert isinstance(some_instance.some_instance, NewClass)
    assert isinstance(some_instance.some_extra_instance, NewClass2)
    instance1 = some_instance.some_instance
    instance2 = some_instance.some_extra_instance

    assert instance1 is not instance2
