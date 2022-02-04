from haps import scopes
from haps.container import (INSTANCE_SCOPE, PROFILES, SINGLETON_SCOPE,
                            Container, Egg, Inject, base, egg, inject, scope)

DI = Container

__all__ = ['Container', 'Inject', 'inject', 'base', 'egg', 'INSTANCE_SCOPE',
           'SINGLETON_SCOPE', 'scope', 'Egg', 'scopes', 'PROFILES', 'DI']
