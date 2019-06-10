import os
from functools import partial
from threading import RLock
from types import FunctionType
from typing import Any, Optional, Type

from haps.exceptions import ConfigurationError, UnknownConfigVariable

_NONE = object()


def _env_resolver(var_name: str, env_name: str = None,
                  default: Any = _NONE) -> Any:
    try:
        return os.environ[env_name or f'HAPS_{var_name}']
    except KeyError:
        if default is not _NONE:
            if callable(default):
                return default()
            else:
                return default
        else:
            raise UnknownConfigVariable


class Configuration:
    """
    Configuration container, a simple object to manage application config
    variables.
    Variables can be set manually, from the environment, or resolved
    via custom function.

    """

    _lock = RLock()
    _instance: 'Configuration' = None

    def __new__(cls, *args, **kwargs) -> 'Configuration':
        with cls._lock:
            if cls._instance is None:
                cls._instance = object.__new__(cls)
                cls._instance.cache = {}
                cls._instance.resolvers = {}
            return cls._instance

    def _resolve_var(self, var_name: str) -> Any:
        if var_name in self.resolvers:
            return self.resolvers[var_name]()
        else:
            raise UnknownConfigVariable(
                f'No resolver registered for {var_name}')

    def get_var(self, var_name: str, default: Optional[Any] = _NONE) -> Any:
        """
        Get a config variable. If a variable is not set, a resolver is not
        set, and no default is given
        :class:`~haps.exceptions.UnknownConfigVariable` is raised.

        :param var_name: Name of variable
        :param default: Default value
        :return: Value of config variable
        """
        try:
            return self.cache[var_name]
        except KeyError:
            try:
                var = self._resolve_var(var_name)
            except UnknownConfigVariable as e:
                if default is not _NONE:
                    if callable(default):
                        return default()
                    else:
                        return default
                else:
                    raise e
            else:
                self.cache[var_name] = var
                return var

    @classmethod
    def resolver(cls, var_name: str) -> FunctionType:
        """
        Variable resolver decorator. Function or method decorated with it is
        used to resolve the config variable.

        .. note::
            Variable is resolved only once.
            Next gets are returned from the cache.

        :param var_name: Variable name
        :return: Function decorator
        """
        def dec(f):
            if var_name in cls().resolvers:
                raise ConfigurationError(
                    f'Resolver for {var_name} already registered')
            cls().resolvers[var_name] = f
            return f

        return dec

    @classmethod
    def env_resolver(cls, var_name: str, env_name: str = None,
                     default: Any = _NONE) -> 'Configuration':
        """
        Method for configuring environment resolver.

        :param var_name: Variable name
        :param env_name: An optional environment variable name. If not set\
            haps looks for `HAPS_var_name`
        :param default: Default value for variable. If it's a callable,\
            it is called before return. If not provided\
            :class:`~haps.exceptions.UnknownConfigVariable` is raised
        :return: :class:`~haps.config.Configuration` instance for easy\
                  chaining
        """

        cls.resolver(var_name)(
            partial(
                _env_resolver, var_name=var_name, env_name=env_name,
                default=default))
        return cls()

    @classmethod
    def set(cls, var_name: str, value: Any) -> 'Configuration':
        """
        Set the variable

        :param var_name: Variable name
        :param value: Value of variable
        :return: :class:`~haps.config.Configuration` instance for easy\
                  chaining
        """
        with cls._lock:
            if var_name not in cls().cache:
                cls().cache[var_name] = value
            else:
                raise ConfigurationError(
                    f'Value for {var_name} already set')
        return cls()


class Config:
    """
    Descriptor providing config variables as a class properties.

    .. code-block:: python

        class SomeClass:
            my_var: VarType = Config()
            custom_property_name: VarType = Config('var_name')

    """
    def __init__(self, var_name: str = None, default=_NONE) -> None:
        """

        :param var_name: An optional variable name. If not set the property\
                name is used.
        :param default: Default value for variable. If it's a callable,\
            it is called before return. If not provided\
            :class:`~haps.exceptions.UnknownConfigVariable` is raised
        """
        self._default = default
        self._var_name = var_name
        self._type = None
        self._name = None

    def __get__(self, instance: 'Config', owner: Type) -> Any:
        var = Configuration().get_var(self._var_name, self._default)
        setattr(instance, self._var_name, var)
        return var

    def __set_name__(self, owner: Type, name: str) -> None:
        self._name = name
        if self._var_name is None:
            self._var_name = name
