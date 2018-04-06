.. _quickstart:

QuickStart
=================================

Here's a simple tutorial how to write your first application using *chaps*.
Assuming you are already created environment with python 3.6+ and installed
chaps, you can start writing some juicy code.


Application layout
---------------------------------

Since chaps doesn't really enforce any project/code design (you can use it even
as an addition to your existing django or flask application!) this is just an
example layout. You will going to create a simple user registration system.

.. code-block:: text

    quickstart/
    ├── setup.py
    └── user_module/
        ├── app.py
        ├── core
        │   ├── implementations/
        │   │   ├── __init__.py
        │   │   ├── db.py
        │   │   └── others.py
        │   ├── __init__.py
        │   └── interfaces.py
        └── __init__.py


Interfaces
-------------------------------

Let's start with creating some interfaces, so we can keep our code clean and
readable:

.. code-block:: python

    # quickstart/user_module/core/interfaces.py
    from chaps import base


    @base
    class IUserService:
        def create_user(self, username: str) -> bool:
            raise NotImplementedError

        def delete_user(self, username: str) -> bool:
            raise NotImplementedError


    @base
    class IDatabase:
        def add_object(self, bucket: str, name: str, data: dict) -> bool:
            raise NotImplementedError

        def delete_object(self, bucket: str, name) -> bool:
            raise NotImplementedError


    @base
    class IMailer:
        def send(self, email: str, message: str) -> None:
            raise NotImplementedError

There are three interfaces:

- :code:`IUserService`: High-level interface with methods to create and delete user
- :code:`IDatabase`: Low-level data repository
- :code:`IMailer`: Just one-method interface for mailing integration

You need to tell *chaps* about your interfaces by using :code:`@base` class decorator,
so it can resolve dependencies correctly.


.. note::
    Be aware that you don't have to create a fully-featured interface, instead
    you can just define a base type, that's enough for *chaps*:

    .. code-block:: python

        @base
        class IUserService:
            pass

    However it's a good practice to do so.


Implementations
------------------------

Every interface should have at least one implementation. So,
we will start with UserService and Mailer implementation.

.. code-block:: python

    # quickstart/user_module/core/interfaces.py
    from chaps import egg, Inject

    from user_module.core.interfaces import IDatabase, IMailer, IUserService


    @egg()
    class DummyMailer(IMailer):
        def send(self, email: str, message: str) -> None:
            print(f'Mail to {email}: {message}')


    @egg()
    class UserService(IUserService):
        db: IDatabase = Inject()
        mailer: IMailer = Inject()

        _bucket = 'users'

        def create_user(self, username: str) -> bool:
            email = f'{username}@my-service.com'
            created = self.db.add_object(self._bucket, username, {
                'email': email
            })
            if created:
                self.mailer.send(email, f'Hello {username}!')
            return created

        def delete_user(self, username: str) -> bool:
            return self.db.delete_object(self._bucket, username)

There are two classes, the first one is very simple, it inherits from
:code:`IMailer` and implements its only method :code:`send`. The only new
thing here is the :code:`@egg()` decorator. You can use is to tell *chaps* about any
callable (a class is also a callable) that returns the implementation of a base type.
Now you can probably guess how chaps can resolve right dependencies - it looks into
inheritance chain.

The :code:`UserService` implementation is a way more interesting. Besides the parts
we've already seen in the :code:`DummyMailer`  implementation, it uses the
:code:`Inject` `descriptor <https://docs.python.org/3.6/howto/descriptor.html>`_ to provide
dependencies. Yes, it's that simple. You just need to define class-level field :code:`Inject`
with proper annotation, and *chaps* will take care of everything else. It means
creation and binding proper instance.

.. warning::
    With this method, the instance of injected class, e.g. DummyMailer, will be
    created (or get) at the time of first property access, and will be assigned
    to the current :code:`UserService` instance.

    So:

    .. code-block:: python

        us = UserService()
        assert us.mailer == us.mailer  # it's always true
        # but
        assert us.mailer == UserService().mailer  # not necessarily
        # (but it can, as you will see later)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
