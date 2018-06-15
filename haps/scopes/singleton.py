from typing import Any, Callable

from haps.scopes import Scope


class SingletonScope(Scope):
    """
    Dependencies within SingletonScope are created only once in
    the application context.
    """

    _objects = {}

    def get_object(self, type_: Callable) -> Any:
        if type_ in self._objects:
            return self._objects[type_]
        else:
            obj = type_()
            self._objects[type_] = obj
            return obj
