import pytest

import haps
from haps import exceptions
from haps.config import Configuration
from haps.exceptions import ConfigurationError
from haps.scopes.instance import InstanceScope


def test_configure():
    haps.Container.configure([])

    assert haps.Container()


def test_already_configured():
    haps.Container.configure([])

    with pytest.raises(exceptions.AlreadyConfigured):
        haps.Container.configure([])


def test_not_configured():
    with pytest.raises(exceptions.NotConfigured):
        haps.Container()


def test_configure_class_and_get_object(some_class):
    haps.Container.configure([
        haps.Egg(some_class, some_class, None, some_class)
    ])

    some_instance = haps.Container().get_object(some_class)
    assert isinstance(some_instance, some_class)


def test_inject_class(some_class):
    haps.Container.configure([
        haps.Egg(some_class, some_class, None, some_class)
    ])

    class AnotherClass:
        @haps.inject
        def __init__(self, some_class_instance: some_class):
            self.some_class_instance = some_class_instance

    some_instance = AnotherClass()

    assert isinstance(some_instance.some_class_instance, some_class)


class GlobalClass:
    pass


def test_inject_with_global_runtime_type_annotation():
    haps.Container.configure([
        haps.Egg(GlobalClass, GlobalClass, None, GlobalClass),
    ])

    class AnotherClass:
        @haps.inject
        def __init__(self, global_class_instance: 'GlobalClass'):
            self.global_class_instance = global_class_instance

    some_instance = AnotherClass()

    assert isinstance(some_instance.global_class_instance, GlobalClass)


def test_inject_with_local_runtime_type_annotation(some_class):
    haps.Container.configure([
        haps.Egg(some_class, some_class, None, some_class),
    ])

    class AnotherClass:
        @haps.inject
        def __init__(self, some_class_instance: 'some_class'):
            self.some_class_instance = some_class_instance

    some_instance = AnotherClass()

    assert isinstance(some_instance.some_class_instance, some_class)


def test_inject_into_function_with_optional_args(some_class):
    haps.Container.configure([
        haps.Egg(some_class, some_class, None, some_class)
    ])

    class NotRegistered:
        pass

    @haps.inject
    def func(some_class_instance: some_class, no_annotation,
             not_registered: NotRegistered):
        return some_class_instance, no_annotation, not_registered

    not_reg = NotRegistered()
    sci, na, nr = func(no_annotation=5, not_registered=not_reg)

    assert isinstance(sci, some_class)
    assert na == 5
    assert nr is not_reg


def test_not_existing_scope():
    @haps.scope('custom')
    class CustomScopedCls:
        pass

    haps.Container.configure([
        haps.Egg(CustomScopedCls, CustomScopedCls, None, CustomScopedCls)
    ])

    class AnotherClass:
        @haps.inject
        def __init__(self, csc: CustomScopedCls):
            pass

    with pytest.raises(exceptions.UnknownScope):
        AnotherClass()


def test_custom_scope():
    @haps.scope('custom')
    class CustomScopedCls:
        pass

    class CustomScope(InstanceScope):
        get_object_called = False

        def get_object(self, type_):
            CustomScope.get_object_called = True
            return super(CustomScope, self).get_object(type_)

    haps.Container.configure([
        haps.Egg(CustomScopedCls, CustomScopedCls, None, CustomScopedCls)
    ])
    haps.Container().register_scope('custom', CustomScope)

    class AnotherClass:
        @haps.inject
        def __init__(self, csc: CustomScopedCls):
            self.csc = csc

    some_instance = AnotherClass()
    assert isinstance(some_instance.csc, CustomScopedCls)
    assert CustomScope.get_object_called


def test_inject_class_using_property_instance_annotation(some_class):
    class NewClass(some_class):
        pass

    haps.Container.configure([
        haps.Egg(some_class, some_class, None, NewClass)
    ])

    class AnotherClass:
        injected_instance: some_class = haps.Inject()

    some_instance = AnotherClass()

    assert hasattr(some_instance, 'injected_instance')
    assert isinstance(some_instance.injected_instance, NewClass)
    instance1 = some_instance.injected_instance
    instance2 = some_instance.injected_instance

    assert instance1 is instance2


def test_inject_class_using_init_annotation(some_class):
    class NewClass(some_class):
        pass

    haps.Container.configure([
        haps.Egg(some_class, some_class, None, NewClass)
    ])

    class AnotherClass:
        @haps.inject
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

    haps.Container.configure([
        haps.Egg(some_class, NewClass, None, NewClass),
        haps.Egg(some_class, NewClass2, 'extra', NewClass2)
    ])

    class AnotherClass:
        some_instance: some_class = haps.Inject()
        some_extra_instance: some_class = haps.Inject('extra')

    some_instance = AnotherClass()

    assert isinstance(some_instance.some_instance, NewClass)
    assert isinstance(some_instance.some_extra_instance, NewClass2)
    instance1 = some_instance.some_instance
    instance2 = some_instance.some_extra_instance

    assert instance1 is not instance2


def test_autodiscovery():
    from samples.autodiscover.sample import (CoffeeMaker, IPump, IHeater)
    haps.Container.autodiscover(['samples.autodiscover.services'])

    cm = CoffeeMaker()
    assert isinstance(cm.pump, IPump)
    assert isinstance(cm.heater, IHeater)


def test_ambiguous_dependency(some_class):
    class NewClass(some_class):
        pass

    class NewClass2(some_class):
        pass

    with pytest.raises(ConfigurationError) as e:
        haps.Container.configure([
            haps.Egg(some_class, some_class, None, NewClass),
            haps.Egg(some_class, some_class, None, NewClass2)
        ])

    assert e.value.args[0] == f'Ambiguous implementation {repr(some_class)}'


@pytest.mark.parametrize("profiles,expected", [
    ((), 'NewClass'),
    (('test',), 'NewClass2'),
    (['prod'], 'NewClass3'),
    (['non-existing', 'test'], 'NewClass2'),
    (('non-existing', 'test', 'prod'), 'NewClass2'),
    (('non-existing', 'prod', 'test'), 'NewClass3')
])
def test_dependencies_with_profiles(some_class, profiles, expected):
    class NewClass(some_class):
        pass

    class NewClass2(some_class):
        pass

    class NewClass3(some_class):
        pass

    Configuration().set('haps.profiles', profiles)
    haps.Container.configure([
        haps.Egg(some_class, NewClass, None, NewClass),
        haps.Egg(some_class, NewClass2, None, NewClass2, 'test'),
        haps.Egg(some_class, NewClass3, None, NewClass3, 'prod')
    ])

    class AnotherClass:
        some_instance: some_class = haps.Inject()

    some_instance = AnotherClass()

    assert type(some_instance.some_instance).__name__ == expected
