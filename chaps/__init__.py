import inspect

from chaps.scope.instance import InstanceScope
from chaps.scope.singleton import SingletonScope

INSTANCE_SCOPE = '__instance'  # default scope
SINGLETON_SCOPE = '__singleton'

try:
    get_argspec = inspect.getfullargspec
except AttributeError:  # python2
    get_argspec = inspect.getargspec


class AlreadyConfigured(Exception):
    pass


class NotConfigured(Exception):
    pass


class UnknownDependency(TypeError):
    pass


class UnknownScope(TypeError):
    pass


class Container(object):
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

    def get_object(self, name):
        try:
            class_ = self.config[name]
        except KeyError:
            raise UnknownDependency('Unknown dependency %s' % name)

        scope_id = getattr(class_, '__chaps_custom_scope', INSTANCE_SCOPE)

        try:
            scope = self.scopes[scope_id]
        except KeyError:
            raise UnknownScope('Unknown scope with id %s' % scope_id)

        return scope.get_object(class_)

    def register_scope(self, name, scope_class):
        if name in self.scopes:
            raise AlreadyConfigured('Scope %s already registered' % name)
        self.scopes[name] = scope_class()

    def register_object(self, name, class_):
        self.config[name] = class_

    @classmethod
    def configure(cls, conf, subclass=None):
        if cls.__configured:
            raise AlreadyConfigured
        else:
            cls.__configured = True
        cls.__subclass = subclass

        container = Container()
        container.config = {}
        container.scopes = {}

        for name, class_ in conf.items():
            container.register_object(name, class_)

        container.register_scope(INSTANCE_SCOPE, InstanceScope)
        container.register_scope(SINGLETON_SCOPE, SingletonScope)


def inject_function(f):
    args = get_argspec(f).args

    def _inner(self):
        container = Container()
        objects = {}
        for arg in args:
            if arg in ('self',):
                continue
            obj = container.get_object(arg)
            objects[arg] = obj
            setattr(self, arg, obj)
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
    def __dec(cls):
        cls.__chaps_custom_scope = scope_type
        return cls

    return __dec


class Inject(object):
    def __init__(self, name):
        self.name = name
        self.__prop_name = '__chaps_%s_%s_instance' % (name, id(self))

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            obj = getattr(self, self.__prop_name, None)
            if obj is None:
                obj = Container().get_object(self.name)
                setattr(instance, self.__prop_name, obj)
            return obj
