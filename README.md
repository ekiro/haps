# chaps [![PyPI](https://img.shields.io/pypi/pyversions/chaps.svg)](https://pypi.python.org/pypi/chaps/) [![Build Status](https://travis-ci.org/ekiro/chaps.svg?branch=master)](https://travis-ci.org/ekiro/chaps)
Chaps is a simple dependency injection library written in pure python (no dependencies).

# Installation

    pip install chaps

# Quick start


First of all, on the beginning of your application, you have to configure
DI container:

### 1. Configuration dict

```python
from chaps import Container

Container.configure({
    Heater: Heater
})
```

`heater` is a dependency name, and `Heater` is a class that will be
instantiated and injected. `

### 2. Autodiscover

You can also let chaps to find and configure dependencies automatically:


```python
# core/iheater.py
from chaps import base

@base
class IHeater:
    ...


# core/heater.py
from chaps import dependency

from core.iheater import IHeater

@dependency
class Heater(IHeater):
    ...


# main.py
from chaps import Container

Container.autodiscover('myapp.core')
```



Then, you should prepare your class. There are coulpe ways to do it:

### 1. `__init__` decorator with annotations

```python
from chaps import inject

Container.configure({
    IHeater: Heater  # Why not interface?
})

class CoffeeMaker(object):
    @inject
    def __init__(self, heater: IHeater):
        self.heater = heater
```

### 2. Property

Remember, a property is a lazy way to inject instance. `get_object` method from
scope will be called when `Inject` property will be accessed for the first time.
With previous methods, objects are injected at instance initialization stage.


```python
from chaps import Container, Inject


Container.configure({
    Heater: Heater
})

class CoffeeMaker(object):
    heater: Heater = Inject()
```


## Done!

That's it. Now you can inject heater instance transparently.

```python
assert isinstance(CoffeMaker().heater, Heater)  # It's true!
```

## Scope

There are two registered scopes:

- `chaps.INSTANCE_SCOPE` - every new instance has its own, fresh object instance (default)
- `chaps.SINGLETON_SCOPE` - there is only one instance of the class in the application context

There are also not registered scopes:
- `chaps.scope.thread.ThreadScope` - Only one instance in the thread context

If the scope is not registered (or you have created your own) you have to
register it before use:

```python
from chaps.scope.thread import ThreadScope

THREAD_SCOPE = '__thread_scope'  # Scope identifier

Container().register_scope(THREAD_SCOPE, ThreadScope)  # After configuration
```


To set class scope, just use `scope` decorator:

```python
from chaps import scope, SINGLETON_SCOPE

@scope(SINGLETON_SCOPE)
class ExtraPump(object):
    pass
```

## Profiles and qualifiers

TODO

For the


# Usage examples

See https://github.com/ekiro/chaps/tree/master/samples

# Testing

Install `requirements.test.txt` and run `py.test` in main directory.

# Changelog

## 4.0

- Drop support for python <3.6
- Add annotation based injects

## 5.0

- Add autodiscover bases and dependencies with `@base` and `@dependency` decorator
- Add named dependencies

# TODO

- Better documentation
