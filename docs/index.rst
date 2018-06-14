.. chaps documentation master file, created by
   sphinx-quickstart on Thu Apr  5 18:13:43 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to chaps documentation!
=================================

*Chaps* is a simple DI library, with IoC container included. It is written in
pure Python with no external dependencies.

Look how easy it is to use:

.. code-block:: python

    from chaps import Container as IoC, Inject, inject

    # import interfaces
    from my_application.core import IDatabase, IUserService


    class MyApp:
        db: IDatabase = Inject()  # dependency as a property

        @inject  # or passed to the constructor
        def __init__(self, user_service: IUserService) -> None:
            self.user_service = user_service

    IoC.autodiscover('my_application')  # find all interfaces and implementations

    if __name__ == '__main__':
        app = MyApp()
        assert isinstance(app.db, IDatabase)
        assert isinstance(app.user_service, IUserService)

Features
--------

- IoC container
- No XML/JSON/YAML - pure python configuration
- No dependencies
- Based on the Python 3.6+ annotation system

Installation
------------

Install *chaps* by running:

.. code::

    pip install chaps

Contribute
----------

- Issue Tracker: github.com/ekiro/chaps/issues
- Source Code: github.com/ekiro/chaps

Support
-------

If you are having issues, ask a question on projects issue tracker.


License
-------

The project is licensed under the MIT license.



.. toctree::
   :maxdepth: 2
   :caption: Contents:

   guide



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
