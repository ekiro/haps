import pytest

import haps
from haps import exceptions
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
        haps.Egg(some_class, some_class, None, NewClass),
        haps.Egg(some_class, some_class, 'extra', NewClass2)
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
