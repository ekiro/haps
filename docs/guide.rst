.. _quickstart:

QuickStart
=================================

Here's a simple tutorial on how to write your first application using *haps*.
Assuming you have already created an environment with python 3.6+ and *haps* installed,
you can start writing some juicy code.


Application layout
---------------------------------

Since *haps* doesn't enforce any project/code design (you can use it
even as an addition to your existing Django or flask application!), this is just an
example layout. You are going to create a simple user registration system.


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
    from haps import base


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

- :code:`IUserService`: High-level interface with methods to create and delete users
- :code:`IDatabase`: Low-level data repository
- :code:`IMailer`: One-method interface for mailing integration

You need to tell *haps* about your interfaces by using :code:`@base` class decorator,
so it can resolve dependencies correctly.


.. note::
    Be aware that you don't have to create a fully-featured interface, instead
    you can just define a base type, that's enough for *haps*:

    .. code-block:: python

        @base
        class IUserService:
            pass

    However, it's a good practice to do so.


Implementations
------------------------

Every interface should have at least one implementation. So,
we will start with UserService and Mailer implementation.

.. code-block:: python

    # quickstart/user_module/core/implementations/others.py
    from haps import egg, Inject

    from user_module.core.interfaces import IDatabase, IMailer, IUserService


    @egg
    class DummyMailer(IMailer):
        def send(self, email: str, message: str) -> None:
            print(f'Mail to {email}: {message}')


    @egg
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

There are two classes, and the first one is quite simple, it inherits from
:code:`IMailer` and implements its only method :code:`send`. The only new
thing here is the :code:`@egg` decorator. You can use it to tell *haps* about any
callable (a class is also a callable) that returns the implementation of a base type.
Now you can probably guess how *haps* can resolve right dependencies - it looks into
inheritance chain.

The :code:`UserService` implementation is a way more interesting. Besides the parts
we've already seen in the :code:`DummyMailer`  implementation, it uses the
:code:`Inject` `descriptor <https://docs.python.org/3.6/howto/descriptor.html>`_ to provide
dependencies. Yes, it's that simple. You only need to define class-level field :code:`Inject`
with proper annotation, and *haps* will take care of everything else. It means
creating and binding the proper instance.

.. warning::
    With this method, the instance of an injected class, e.g., DummyMailer, is
    created (or fetched from the container) at the time of first property access,
    and then is assigned to the current :code:`UserService` instance.

    So:

    .. code-block:: python

        us = UserService()
        assert us.mailer is us.mailer  # it's always true
        # but
        assert us.mailer is UserService().mailer  # not necessarily
        # (but it can, as you will see later)


Now let's move to our repository. We need to implement some data storage for our
project. For now, it'll be in-memory storage, but, thanks to haps, you can
quickly switch between many implementations. Creation of the database repository
may be more complicated, so we'll use a factory function.

.. code-block:: python

    # quickstart/user_module/core/implementations/db.py
    from collections import defaultdict

    from haps import egg, scope, SINGLETON_SCOPE

    from user_module.core.interfaces import IDatabase


    class InMemoryDb(IDatabase):
        storage: dict

        def __init__(self):
            self.storage = defaultdict(dict)

        def add_object(self, bucket: str, name: str, data: dict) -> bool:
            if name in self.storage[bucket]:
                return False
            else:
                self.storage[bucket][name] = data
                return True

        def delete_object(self, bucket: str, name) -> bool:
            try:
                del self.storage[bucket][name]
            except KeyError:
                return False
            else:
                return True


    @egg
    @scope(SINGLETON_SCOPE)
    def database_factory() -> IDatabase:
        db = InMemoryDb()
        # Maybe do some stuff, like reading configuration
        # or create some kind of db-session.
        return db


:code:`InMemoryDb` is a simple implementation of :code:`IDatabase` that uses
defaultdict to store users. It could be file-based storage or even SQL storage.
However, notice there's no :code:`@egg` decorator on this implementation. Instead,
we've created a function decorated with it which have :code:`IDatabase`
declared as the return type.

In this case, when injecting, haps calls :code:`database_factory` function
and injects the result.


.. warning::
    Be aware that *haps* by design WILL NOT validate function output in any way.
    So if your function returns a type that's not compatible with declared one,
    it could lead to hard to catch errors.


Scope
-----------------

As you can see in the previous file, :code:`database_factory` function
is also decorated with :code:`scope` decorator.

A scope in *haps* determines object life-cycle. The default scope is :code:`INSTANCE_SCOPE`,
and you don't have to declare it explicitly. There are also two scopes that ships with
haps, :code:`SINGLETON_SCOPE`, and :code:`THREAD_SCOPE`. You can also create your own
scopes. You can read about scopes in another chapter, but for the clarity:
:code:`SINGLETON_SCOPE` means that *haps* creates only one instance, and injects
the same object every time. On the other hand, dependencies with
:code:`INSTANCE_SCOPE` (which is default), are instantiated on every injection.


Run the code!
------------------

Now we have configured our interfaces and dependencies, and we're ready to
run our application:

.. code-block:: python

    # quickstart/user_module/app.py
    from haps import Container as IoC, inject

    from user_module.core.interfaces import IUserService


    class UserModule:
        @inject
        def __init__(self, user_service: IUserService) -> None:
            self.user_service = user_service

        def register_user(self, username: str) -> None:
            if self.user_service.create_user(username):
                print(f'User {username} created!')
            else:
                print(f'User {username} already exists!')

        def delete_user(self, username: str) -> None:
            if self.user_service.delete_user(username):
                print(f'User {username} deleted!')
            else:
                print(f'User {username} does not exists!')


    IoC.autodiscover(['user_module.core'])

    if __name__ == '__main__':
        um = UserModule()
        um.register_user('Kiro')
        um.register_user('John')
        um.register_user('Kiro')
        um.delete_user('Kiro')
        um.delete_user('Kiro')
        another_um_instance = UserModule()
        another_um_instance.register_user('John')


The main class :code:`UserModule` takes :code:`IUserService` in the constructor,
and thanks to the :code:`@inject` decorator, haps will create and
pass :code:`UserService` instance to it.

After that, we have to call :code:`autodiscover` method from *haps*, which
scans all modules under given path and configures all dependencies.

Running our application should give following output:

.. code-block:: text

    Mail to Kiro@my-service.com: Hello Kiro!
    User Kiro created!
    Mail to John@my-service.com: Hello John!
    User John created!
    User Kiro already exists!
    User Kiro deleted!
    User Kiro does not exists!
    User John already exists!
