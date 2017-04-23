import inspect

from chaps.scope.instance import InstanceScope
from chaps.scope.singleton import SingletonScope

INSTANCE_SCOPE = '__instance'  # default scope
SINGLETON_SCOPE = '__singleton'


class AlreadyConfigured(Exception):
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
        if cls.__instance is None:
            class_ = cls if cls.__subclass is None else cls.__subclass
            cls.__instance = object.__new__(class_)
        return cls.__instance

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


def inject(f):
    args = inspect.getfullargspec(f).args

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


def scope(scope_type):
    def __dec(cls):
        cls.__chaps_custom_scope = scope_type
        return cls

    return __dec
