from threading import local
from typing import Any, Callable

from haps.scopes import Scope


class ThreadScope(Scope):
    """
    Dependencies within ThreadScope are created only once in a thread
    context.
    """

    _thread_local = local()

    def get_object(self, type_: Callable) -> Any:
        try:
            objects = self._thread_local.objects
        except AttributeError:
            objects = {}
            self._thread_local.objects = objects

        if type_ in objects:
            return objects[type_]
        else:
            obj = type_()
            objects[type_] = obj
            return obj
