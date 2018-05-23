import importlib
import inspect
import pkgutil
import sys

from chaps.configparser import ConfigParser
from chaps.scope.instance import InstanceScope
from chaps.scope.singleton import SingletonScope

INSTANCE_SCOPE = '__instance'  # default scope
SINGLETON_SCOPE = '__singleton'


class AlreadyConfigured(Exception):
    pass


class ConfigurationError(Exception):
    pass


class NotConfigured(Exception):
    pass


class UnknownDependency(TypeError):
    pass


class UnknownScope(TypeError):
    pass


class Container(object):
    """
    Dependency Injection container class
    """
    __instance = None
    __subclass = None
    __configured = False

    def __new__(cls, *args, **kwargs):
        if not cls.__configured:
            raise NotConfigured
        if cls.__instance is None:
            class_ = cls if cls.__subclass is None else cls.__subclass
            cls.__instance = object.__new__(class_)
        return cls.__instance

    @classmethod
    def _reset(cls):
        """Internal use only."""
        cls.__instance = None
        cls.__configured = False
        cls.__subclass = None

    def get_object(self, type_, qualifier=None):
        """
        Get object instance

        Args:
            type_: a type of requested dependency
            qualifier: name of requested dependency (optional)

        Returns:
            Desired object instance from scope
        """
        try:
            class_ = self.config[(type_, qualifier)]
        except KeyError:
            raise UnknownDependency(
                'Unknown dependency %s [%s]' % (type_, qualifier))

        scope_id = getattr(class_, '__chaps_custom_scope', INSTANCE_SCOPE)

        try:
            _scope = self.scopes[scope_id]
        except KeyError:
            raise UnknownScope('Unknown scope with id %s' % scope_id)

        return _scope.get_object(class_)

    def register_scope(self, name, scope_class):
        """

        Args:
            name: scope identifier
            scope_class: scope class/callable

        Returns:

        """
        if name in self.scopes:
            raise AlreadyConfigured('Scope %s already registered' % name)
        self.scopes[name] = scope_class()

    def register_object(self, type_, class_, qualifier=None):
        self.config[(type_, qualifier)] = class_

    @classmethod
    def configure(cls, conf, subclass=None):
        """
        Configure chaps container

        Args:
            conf: config dictionary
            subclass: optional Container class

        """
        if cls.__configured:
            raise AlreadyConfigured
        else:
            cls.__configured = True
        cls.__subclass = subclass

        container = Container()
        container.config = {}
        container.scopes = {}

        for key, class_ in conf.items():
            if isinstance(key, tuple) and len(key) == 2:
                type_, qualifier = key
            else:
                type_, qualifier = key, None

            container.register_object(type_, class_, qualifier=qualifier)

        container.register_scope(INSTANCE_SCOPE, InstanceScope)
        container.register_scope(SINGLETON_SCOPE, SingletonScope)

    @classmethod
    def autodiscover(cls, path, subclass=None, profiles: set = frozenset()):
        """
        Autodiscover interfaces (bases) and implementations (services) in given
        path.

        Params
            path: import path
        """

        def find_base(bases: set, implementation):
            found = {b for b in bases if issubclass(implementation, b)}
            if not found:
                raise ConfigurationError(
                    "No base defined for %r" % implementation)
            elif len(found) > 1:
                raise ConfigurationError(
                    "More than one base found for %r" % implementation)
            else:
                return found.pop()

        def walk(pkg):
            if isinstance(pkg, str):
                pkg = importlib.import_module(pkg)
            results = {}
            for loader, name, is_pkg in pkgutil.walk_packages(pkg.__path__):
                full_name = pkg.__name__ + '.' + name
                results[full_name] = importlib.import_module(full_name)
                if is_pkg:
                    results.update(walk(full_name))
            return results

        walk(path)

        config = {}
        for type_, qualifier, profile in dependency.implementations:
            if profile is not None:
                if profile.startswith('!'):
                    if profile[1:] in profiles:
                        continue
                elif profile not in profiles:
                    continue
            key = (find_base(base.interfaces, type_), qualifier)
            if key in config:
                raise ConfigurationError(
                    "Ambiguous implementation %s" % repr(key))
            config[key] = type_

        cls.configure(config, subclass=subclass)

    @classmethod
    def configure_from_file(cls, filename, subclass=None):
        config = ConfigParser(filename)
        cls.configure(config.deps(), subclass=subclass)

        for id_, cb in config.scopes().items():
            Container().register_scope(id_, cb)


def inject_function(f):
    full_arg_spec = inspect.getfullargspec(f)
    args = full_arg_spec.args
    annotations = full_arg_spec.annotations

    def _inner(self):
        container = Container()
        objects = {}
        for arg in args:
            if arg in ('self',):
                continue
            try:
                obj_type = annotations[arg]
            except KeyError:
                obj_type = arg
            obj = container.get_object(obj_type)
            objects[arg] = obj
        return f(self, **objects)

    return _inner


def inject(*args):
    if len(args) == 1 and inspect.isfunction(args[0]):
        return inject_function(args[0])
    else:
        def inject_class(cls):
            orig_init = cls.__init__

            def __init__(self, *a, **kw):
                container = Container()
                for arg in args:
                    obj = container.get_object(arg)
                    setattr(self, arg, obj)
                orig_init(self, *a, **kw)

            cls.__init__ = __init__

            return cls

        return inject_class


def scope(scope_type):
    """
    Set scope of an instance
    Params
        scope_type: name of the registered scope
    """

    def __dec(cls):
        cls.__chaps_custom_scope = scope_type
        return cls

    return __dec


def base(interface):
    """
    Mark class as an interface
    Params
        interface: interface class
    """
    base.interfaces.add(interface)
    return interface


base.interfaces = set()


def dependency(cls=None, qualifier: str = None, profile: str = None):
    """
    Mark class as an implementation of some interface
    Params
        cls: implementation class (required)
        qualifier: required if there's another implementation registered
    """
    def __inner(cls_):
        assert cls_ is not None
        dependency.implementations.append((cls_, qualifier, profile))
        return cls_

    if cls:
        return __inner(cls)
    else:
        return __inner


dependency.implementations = list()


class Inject(object):
    def __init__(self, name=None):
        if sys.version_info < (3, 6):
            raise TypeError(
                "__init__() missing 1 required positional argument: "
                "'name'")
        self.name = name
        self._type = None
        self.__prop_name = '__chaps_%s_%s_instance' % (name, id(self))

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            obj = getattr(instance, self.__prop_name, None)
            if obj is None:
                obj = Container().get_object(self.type_, qualifier=self.name)
                setattr(instance, self.__prop_name, obj)
            return obj

    def __set_name__(self, owner, name):
        type_ = owner.__annotations__.get(name)
        if type_ is not None:
            self.type_ = type_
        else:
            raise TypeError('No annotation for Inject')
