from typing import Any, List, Type

from haps import Container
from haps.config import Configuration
from haps.exceptions import ConfigurationError


class Application:
    """
    Base Application class that should be the entry point for haps
    applications. You can override `__main__` to inject dependencies.
    """

    @classmethod
    def configure(cls, config: Configuration) -> None:
        """
        Method for configure haps application.

        This method is invoked before autodiscover.

        :param config: Configuration instance
        """
        pass

    def run(self) -> None:
        """
        Method for application entry point (like the `main` method in C).
        Must be implemented.
        """
        raise NotImplementedError


class ApplicationRunner:
    @staticmethod
    def run(app_class: Type[Application],
            extra_module_paths: List[str] = None, **kwargs: Any) -> None:
        """
        Runner for haps application.

        :param app_class: :class:`~haps.application.Application` type
        :param extra_module_paths: Extra modules list to autodiscover
        :param kwargs: Extra arguments are passed to\
                :func:`~haps.Container.autodiscover`
        """
        module = app_class.__module__
        if (module == '__main__' and
                extra_module_paths is None and
                'module_paths' not in kwargs):
            raise ConfigurationError(
                'You cannot run application from __main__ module without '
                'providing module_paths')

        if module != '__main__':
            module_paths = [app_class.__module__]
        else:
            module_paths = []

        if extra_module_paths is not None:
            module_paths.extend(extra_module_paths)
        autodiscover_kwargs = {
            'module_paths': module_paths,
        }
        autodiscover_kwargs.update(kwargs)

        app_class.configure(Configuration())

        Container.autodiscover(**autodiscover_kwargs)

        app = app_class()
        app.run()
