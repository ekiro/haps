from typing import Any, List, Type

from haps import Container
from haps.exceptions import ConfigurationError


class Application:
    """
    Base Application class that should be the entrupoint for haps
    applications. You can override `__main__` to inject dependencies.
    """

    def run(self) -> None:
        """
        Method for application entrypoint (like the `main` method in C).
        You should override this.
        """
        raise NotImplementedError


class ApplicationRunner:
    @staticmethod
    def run(app_class: Type[Application],
            extra_module_paths: List[str] = None, **kwargs: Any) -> None:
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

        Container.autodiscover(**autodiscover_kwargs)

        app = app_class()
        app.run()
