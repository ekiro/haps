from typing import Any, Callable


class Scope:
    """
    Base scope class. Every custom scope should subclass this.
    """

    def get_object(self, type_: Callable) -> Any:
        """
        Returns object from scope
        :param type_:
        """
        raise NotImplementedError
