try:
    import contextvars
except ImportError:
    raise RuntimeError(
        "Context scope can be used only with python >=3.7")
from functools import wraps
from types import FunctionType
from typing import Any, Callable, Dict

from haps.scopes import Scope


class ContextScope(Scope):
    """
    Dependencies within ContextScpoe are created only once in a given
    context.
    """

    _context = contextvars.ContextVar('objects')

    def get_object(self, type_: Callable) -> Any:
        objects: Dict = self._context.get()

        if type_ in objects:
            return objects[type_]
        else:
            obj = type_()
            objects[type_] = obj
            return obj

    @classmethod
    def with_context(cls, f) -> FunctionType:
        @wraps(f)
        def _inner(*args, **kwargs):
            token = cls._context.set({})
            ret = f(*args, **kwargs)
            cls._context.reset(token)
            return ret

        return _inner
