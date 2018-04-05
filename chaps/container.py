import importlib
import inspect
import pkgutil
from functools import singledispatch, wraps
from inspect import Signature
from threading import RLock
from types import FunctionType, ModuleType
from typing import (Any, Callable, Dict, Hashable, List, Optional, Type,
                    TypeVar, Union)

from chaps.exceptions import (AlreadyConfigured, CallError, ConfigurationError,
                              NotConfigured, UnknownDependency, UnknownScope)
from chaps.scope import Scope
from chaps.scope.instance import InstanceScope
from chaps.scope.singleton import SingletonScope

INSTANCE_SCOPE = '__instance'  # default scope
SINGLETON_SCOPE = '__singleton'

T = TypeVar("T")


class Egg:
    base_: Optional[Type]
    type_: Type
    qualifier: Optional[str]
    egg: Callable

    def __init__(self, base_: Optional[Type], type_: Type,
                 qualifier: Optional[str], egg: Callable) -> None:
        self.base_ = base_
        self.type_ = type_
        self.qualifier = qualifier
        self.egg = egg

    def __repr__(self):
        return (f'<chaps.container.Egg base_={repr(self.base_)} '
                f'type_={repr(self.type_)} qualifier={repr(self.qualifier)} '
                f'egg={repr(self.egg)}>')


class Container:
    """
    Dependency Injection container class
    """
    __instance = None
    __subclass = None
    __configured = False
    _lock = RLock()

    def __new__(cls, *args, **kwargs) -> 'Container':
        with cls._lock:
            if not cls.__configured:
                raise NotConfigured
            if cls.__instance is None:
                class_ = cls if cls.__subclass is None else cls.__subclass
                cls.__instance = object.__new__(class_)
                cls.__instance.scopes: Dict[Hashable, Scope] = {}
                cls.__instance.config: List[Egg] = []

            return cls.__instance

    @classmethod
    def _reset(cls):
        cls.__instance = None
        cls.__subclass = None
        cls.__configured = False

    @staticmethod
    def configure(
            config: List[Egg], subclass: 'Container' = None) -> None:
        with Container._lock:
            if Container.__configured:
                raise AlreadyConfigured
            if subclass is None:
                subclass = Container

            Container.__subclass = subclass
            Container.__configured = True

            container = Container()
            if not all(isinstance(o, Egg) for o in config):
                raise ConfigurationError('All config items should be the eggs')
            container.config = config

            container.register_scope(INSTANCE_SCOPE, InstanceScope)
            container.register_scope(SINGLETON_SCOPE, SingletonScope)

    @classmethod
    def autodiscover(
            cls, module_path: str, subclass=None) -> None:
        def find_base(bases: set, implementation: Type):
            found = {b for b in bases if issubclass(implementation, b)}
            if not found:
                raise ConfigurationError(
                    "No base defined for %r" % implementation)
            elif len(found) > 1:
                raise ConfigurationError(
                    "More than one base found for %r" % implementation)
            else:
                return found.pop()

        def walk(pkg: Union[str, ModuleType]) -> Dict[str, ModuleType]:
            if isinstance(pkg, str):
                pkg: ModuleType = importlib.import_module(pkg)
            results = {}
            for loader, name, is_pkg in pkgutil.walk_packages(pkg.__path__):
                full_name = pkg.__name__ + '.' + name
                results[full_name] = importlib.import_module(full_name)
                if is_pkg:
                    results.update(walk(full_name))
            return results

        walk(module_path)

        config: List[Egg] = []
        configured = set()
        for egg_ in egg.factories:
            base_ = find_base(base.classes, egg_.type_)
            if (base_, egg_.qualifier) in configured:
                raise ConfigurationError(
                    "Ambiguous implementation %s" % repr(base_))
            egg_.base_ = base_
            configured.add((base_, egg_.qualifier))
            config.append(egg_)

        cls.configure(config, subclass=subclass)

    def _find_egg(self, base_: Type, qualifier: Hashable) -> Optional[Egg]:
        return next((e for e in self.config if
                     e.base_ is base_ and e.qualifier == qualifier), None)

    def get_object(self, base_: Type, qualifier: Hashable = None) -> Any:
        egg_ = self._find_egg(base_, qualifier)
        if egg_ is None:
            raise UnknownDependency(
                'Unknown dependency %s' % base_)

        scope_id = getattr(egg_.egg, '__chaps_custom_scope', INSTANCE_SCOPE)

        try:
            _scope = self.scopes[scope_id]
        except KeyError:
            raise UnknownScope('Unknown scope with id %s' % scope_id)
        else:
            return _scope.get_object(egg_.egg)

    def register_scope(self, name: Hashable, scope_class: Type[Scope]) -> None:
        if name in self.scopes:
            raise AlreadyConfigured(f'Scope {name} already registered')
        self.scopes[name] = scope_class()


class Inject:
    def __init__(self, qualifier: Hashable = None):
        self._qualifier = qualifier
        self._type: Type = None
        self.__prop_name = '__chaps_%s_%s_instance' % ('', id(self))

    def __get__(self, instance: Any, owner: Type) -> Any:
        if instance is None:
            return self
        else:
            obj = getattr(instance, self.__prop_name, None)
            if obj is None:
                obj = Container().get_object(self.type_, self._qualifier)
                setattr(instance, self.__prop_name, obj)
            return obj

    def __set_name__(self, owner: Type, name: str) -> None:
        type_: Type = owner.__annotations__.get(name)
        if type_ is not None:
            self.type_ = type_
        else:
            raise TypeError('No annotation for Inject')


def inject(fun: Callable) -> Callable:
    sig = inspect.signature(fun)

    injectables: Dict[str, Any] = {}
    for name, param in sig.parameters.items():
        type_ = param.annotation
        if type_ is Signature.empty:
            continue
        else:
            injectables[name] = type_

    @wraps(fun)
    def _inner(*args, **kwargs):
        if len(args) > 1:
            raise CallError('Cannot call this method with arguments ')
        container = Container()
        for n, t in injectables.items():
            if name not in kwargs:
                kwargs[n] = container.get_object(t)

        return fun(*args, **kwargs)

    return _inner


def base(cls: T) -> T:
    base.classes.add(cls)
    return cls


base.classes = set()

Factory_T = Callable[..., T]


def egg(qualifier: Hashable = None):
    @singledispatch
    def egg_dec(_: Any) -> T:
        raise AttributeError('Wrong egg obj type')

    @egg_dec.register(FunctionType)
    def _f(obj: Factory_T) -> Factory_T:
        spec = inspect.signature(obj)
        return_annotation = spec.return_annotation
        if return_annotation is Signature.empty:
            raise ConfigurationError('No return type annotation')
        egg.factories.append(Egg(
            type_=spec.return_annotation,
            qualifier=qualifier,
            egg=obj,
            base_=None,
        ))
        return obj

    @egg_dec.register(Type)
    def _o(obj: T) -> T:  # noqa
        egg.factories.append(Egg(
            type_=obj,
            qualifier=qualifier,
            egg=obj,
            base_=None
        ))
        return obj

    return egg_dec


egg.factories: List[Egg] = []


def scope(scope_type: Hashable) -> Callable:
    def dec(egg_: T) -> T:
        egg_.__chaps_custom_scope = scope_type
        return egg_

    return dec
