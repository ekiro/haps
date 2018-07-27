.. _container:

API
=================================


Container
---------------------------------

.. autoclass:: haps.Container

Container is a heart of *haps*. For now, its implemented as a singleton
that can only be used after one-time configuration.

.. code-block:: python

    from haps import Container

    Container.autodiscover(['my.package'])  # configuration, once in the app lifetime
    Container().some_method()  # Call method on the instance

That means, you can create instances of classes that use injections, only after
*haps* is properly configured.


.. automethod:: haps.Container.autodiscover

.. automethod:: haps.Container.configure

.. automethod:: haps.Container.get_object

.. automethod:: haps.Container.register_scope


Egg
---------------------------------


.. autoclass:: haps.Egg

.. automethod:: haps.Egg.__init__


Injection
---------------------------------

.. autoclass:: haps.Inject

.. autofunction:: haps.inject


Dependencies
---------------------------------

.. autofunction:: haps.base

.. autofunction:: haps.egg

.. autofunction:: haps.scope


Configuration
---------------------------------

.. autoclass:: haps.config.Configuration

.. automethod:: haps.config.Configuration.get_var

.. automethod:: haps.config.Configuration.resolver

.. automethod:: haps.config.Configuration.env_resolver

.. automethod:: haps.config.Configuration.set

.. autoclass:: haps.config.Config

.. automethod:: haps.config.Config.__init__
