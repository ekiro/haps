.. _scopes:

Scopes
=================================

A scope is a special object that controls dependency creation. It
decides if new dependency instance should be created, or some cached
instance should be returned.

By default, there are two scopes registered in haps:
:class:`~haps.scopes.InstanceScope` and :class:`~haps.scopes.SingletonScope`
as :data:`haps.INSTANCE_SCOPE` and :data:`haps.SINGLETON_SCOPE`.
The :data:`haps.INSTANCE_SCOPE` is used as a default.

You can register any other scope by calling
:meth:`haps.Container.register_scope`. New scopes should be a subclass
of :class:`haps.scopes.Scope`.


.. autoclass:: haps.scopes.Scope

.. autoclass:: haps.scopes.instance.InstanceScope

.. autoclass:: haps.scopes.singleton.SingletonScope

.. autoclass:: haps.scopes.thread.ThreadScope
