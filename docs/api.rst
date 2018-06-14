.. _container:

API
=================================


Container
---------------------------------

.. autoclass:: chaps.Container

Container is a heart of *chaps*. For now, its implemented as a singleton
that can only be used after one-time configuration.

.. code-block:: python

    from chaps import Container

    Container.autodiscover(['my.package'])  # configuration, once in the app lifetime
    Container().some_method()  # Call method on the instance

That means, you can create instances of classes that use injections, only after
*chaps* is properly configured.


.. automethod:: chaps.Container.autodiscover

.. automethod:: chaps.Container.configure

.. automethod:: chaps.Container.get_object

.. automethod:: chaps.Container.register_scope


Egg
---------------------------------


.. autoclass:: chaps.Egg

.. automethod:: chaps.Egg.__init__


Injection
---------------------------------

.. autoclass:: chaps.Inject

.. autofunction:: chaps.inject


Dependencies
---------------------------------

.. autofunction:: chaps.egg

.. autofunction:: chaps.scope
