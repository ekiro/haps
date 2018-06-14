# chaps [![PyPI](https://img.shields.io/pypi/pyversions/chaps.svg)](https://pypi.python.org/pypi/chaps/) [![Build Status](https://travis-ci.org/ekiro/chaps.svg?branch=master)](https://travis-ci.org/ekiro/chaps)
Chaps [χaps] is a simple DI library, with IoC container included. It is written in pure Python with no external dependencies.

Look how easy it is to use:

```python
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
```

# Installation

    pip install chaps

# Documentation

See https://chaps.readthedocs.io/en/latest/

# Usage examples

See https://github.com/ekiro/chaps/tree/master/samples

# Testing

Install `requirements.test.txt` and run `py.test` in main directory.

# Changelog

## 1.0.0 (15.06.2018)

First stable release
