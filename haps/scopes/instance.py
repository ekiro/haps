from typing import Any, Callable

from haps.scopes import Scope


class InstanceScope(Scope):
    """
    Dependencies within InstanceScope are created at every injection.
    """

    def get_object(self, type_: Callable) -> Any:
        return type_()
