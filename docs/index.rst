.. haps documentation master file, created by
   sphinx-quickstart on Thu Apr  5 18:13:43 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to haps documentation!
=================================

**Haps** *[χaps]* is a simple DI library, with IoC container included. It is written in
pure Python with no external dependencies.

Look how easy it is to use:

.. code-block:: python

    from haps import Container as IoC, Inject, inject

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

Install *haps* by running:

.. code::

    pip install haps

Contribute
----------

- Issue Tracker: github.com/ekiro/haps/issues
- Source Code: github.com/ekiro/haps

Changelog
---------

1.0.4 (2018-06-30)
.....................

* Add support for python 3.7
* Fix autodiscover sample

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
   api
   scopes
   exceptions



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
