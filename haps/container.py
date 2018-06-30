import importlib
import inspect
import pkgutil
from functools import wraps
from inspect import Signature
from threading import RLock
from types import FunctionType, ModuleType
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

from haps.exceptions import (AlreadyConfigured, CallError, ConfigurationError,
                             NotConfigured, UnknownDependency, UnknownScope)
from haps.scopes import Scope
from haps.scopes.instance import InstanceScope
from haps.scopes.singleton import SingletonScope

INSTANCE_SCOPE = '__instance'  # default scopes
SINGLETON_SCOPE = '__singleton'

T = TypeVar("T")


class Egg:
    """
    Configuration primitive. Can be used to configure *haps* manually.
    """
    base_: Optional[Type]
    type_: Type
    qualifier: Optional[str]
    egg: Callable

    def __init__(self, base_: Optional[Type], type_: Type,
                 qualifier: Optional[str], egg_: Callable) -> None:
        """
        :param base_: `base` of dependency, used for retrieve object
        :param type_: `type` of dependency (for functions it's a return type)
        :param qualifier: extra qualifier for dependency. Can be used to\
            register more than one type for one base.
        :param egg_: any callable that returns an instance of dependency, can\
            be class or function
        """
        self.base_ = base_
        self.type_ = type_
        self.qualifier = qualifier
        self.egg = egg_

    def __repr__(self):
        return (f'<haps.container.Egg base_={repr(self.base_)} '
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
                cls.__instance.scopes: Dict[str, Scope] = {}
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
        """
        Configure haps manually, an alternative
        to :func:`~haps.Container.autodiscover`

        :param config: List of configured Eggs
        :param subclass: Optional Container subclass that should be used
        """
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
            cls, module_paths: List[str], subclass: 'Container' = None
    ) -> None:
        """
        Load all modules automatically and find bases and eggs.

        :param module_paths: List of paths that should be discovered
        :param subclass: Optional Container subclass that should be used
        """

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

        with cls._lock:
            for module_path in module_paths:
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

    def _find_egg(self, base_: Type, qualifier: str) -> Optional[Egg]:
        return next((e for e in self.config if
                     e.base_ is base_ and e.qualifier == qualifier), None)

    def get_object(self, base_: Type, qualifier: str = None) -> Any:
        """
        Get instance directly from the container.

        If the qualifier is not None, proper method to create/retrieve instance
        is  used.

        :param base_: `base` of this object
        :param qualifier: optional qualifier
        :return: object instance
        """
        egg_ = self._find_egg(base_, qualifier)
        if egg_ is None:
            raise UnknownDependency(
                'Unknown dependency %s' % base_)

        scope_id = getattr(egg_.egg, '__haps_custom_scope', INSTANCE_SCOPE)

        try:
            _scope = self.scopes[scope_id]
        except KeyError:
            raise UnknownScope('Unknown scopes with id %s' % scope_id)
        else:
            with self._lock:
                return _scope.get_object(egg_.egg)

    def register_scope(self, name: str, scope_class: Type[Scope]) -> None:
        """
        Register new scopes which should be subclass of `Scope`

        :param name: Name of new scopes
        :param scope_class: Class of new scopes
        """
        with self._lock:
            if name in self.scopes:
                raise AlreadyConfigured(f'Scope {name} already registered')
            self.scopes[name] = scope_class()


class Inject:
    """
    A descriptor for injecting dependencies as properties

    .. code-block:: python

        class SomeClass:
            my_dep: DepType = Inject()

    .. important::

        Dependency is injected (created/fetched) at the moment of attribute
        access, not instance of `SomeClass` creation. So, even if you create
        an instance of `SomeClass`, the instance of `DepType` may never be
        created.
    """

    def __init__(self, qualifier: str = None):
        self._qualifier = qualifier
        self._type: Type = None
        self.__prop_name = '__haps_%s_%s_instance' % ('', id(self))

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
    """
    A decorator for injection dependencies into functions/methods, based
    on their type annotations.

    .. code-block:: python

        class SomeClass:
            @inject
            def __init__(self, my_dep: DepType) -> None:
                self.my_dep = my_dep

    .. important::

        On the opposite to :class:`~haps.Inject`, dependency is injected
        at the moment of method invocation. In case of decorating `__init__`,
        dependency is injected when `SomeClass` instance is created.

    :param fun: callable with annotated parameters
    :return: decorated callable
    """
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
    """
    A class decorator that marks class as a base type.

    :param cls: Some base type
    :return: Not modified `cls`
    """
    base.classes.add(cls)
    return cls


base.classes = set()

Factory_T = Callable[..., T]


def egg(qualifier: str = None):
    """
    A function that returns a decorator that marks class or function as a
    source of `base`.

    If a class is decorated, it should inherit after from `base` type.

    If a function is decorated, it declared return type should inherit after
    some `base` type, or it should be the `base` type.

    .. code-block:: python

        @egg()
        class DepImpl(DepType):
            pass

        @egg(qualifier='special_dep')
        def dep_factory() -> DepType:
            return SomeDepImpl()

    :param qualifier: extra qualifier for dependency. Can be used to\
            register more than one type for one base.
    :return: decorator
    """

    def egg_dec(obj: Union[FunctionType, type]) -> T:
        if isinstance(obj, FunctionType):
            spec = inspect.signature(obj)
            return_annotation = spec.return_annotation
            if return_annotation is Signature.empty:
                raise ConfigurationError('No return type annotation')
            egg.factories.append(Egg(
                type_=spec.return_annotation,
                qualifier=qualifier,
                egg_=obj,
                base_=None,
            ))
            return obj
        elif isinstance(obj, type):
            egg.factories.append(Egg(
                type_=obj,
                qualifier=qualifier,
                egg_=obj,
                base_=None
            ))
            return obj
        else:
            raise AttributeError('Wrong egg obj type')

    return egg_dec


egg.factories: List[Egg] = []


def scope(scope_type: str) -> Callable:
    """
    A function that returns decorator that set scopes to some class/function

    .. code-block:: python

        @egg()
        @scopes(SINGLETON_SCOPE)
        class DepImpl:
            pass

    :param scope_type: Which scope should be used
    :return:
    """

    def dec(egg_: T) -> T:
        egg_.__haps_custom_scope = scope_type
        return egg_

    return dec
