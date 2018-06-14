.. _scopes:

Scopes
=================================

A scope is a special object that controls dependency creation. It
decides if new dependency instance should be created, or some cached
instance should be returned.

By default, there are two scopes registered in chaps:
:class:`~chaps.scopes.InstanceScope` and :class:`~chaps.scopes.SingletonScope`
as :data:`chaps.INSTANCE_SCOPE` and :data:`chaps.SINGLETON_SCOPE`.
The :data:`chaps.INSTANCE_SCOPE` is used as a default.

You can register any other scope by calling
:meth:`chaps.Container.register_scope`. New scopes should be a subclass
of :class:`chaps.scopes.Scope`.


.. autoclass:: chaps.scopes.Scope

.. autoclass:: chaps.scopes.instance.InstanceScope

.. autoclass:: chaps.scopes.singleton.SingletonScope

.. autoclass:: chaps.scopes.thread.ThreadScope
