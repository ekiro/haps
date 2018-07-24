import os
from functools import partial
from threading import RLock
from types import FunctionType
from typing import Any, Type

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
    _lock = RLock()
    _instance: 'Configuration' = None

    def __new__(cls, *args, **kwargs) -> 'Container':
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

    def get_var(self, var_name: str, default: Any = _NONE) -> Any:
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
        def dec(f):
            if var_name in cls().resolvers:
                raise ConfigurationError(
                    f'Resolver for {var_name} already registered')
            cls().resolvers[var_name] = f
            return f

        return dec

    @classmethod
    def env_resolver(cls, var_name: str, env_name: str = None,
                     default: Any = _NONE) -> None:
        cls.resolver(var_name)(
            partial(
                _env_resolver, var_name=var_name, env_name=env_name,
                default=default))

    @classmethod
    def set(cls, var_name: str, value: Any) -> None:
        with cls._lock:
            if var_name not in cls().cache:
                cls().cache[var_name] = value
            else:
                raise ConfigurationError(
                    f'Value for {var_name} already set')


class Config:
    def __init__(self, var_name: str = None, default=_NONE) -> None:
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
