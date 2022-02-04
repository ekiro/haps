# haps [![PyPI](https://badge.fury.io/py/haps.png)](https://pypi.python.org/pypi/haps/) [![Build Status](https://travis-ci.org/lunarwings/haps.svg?branch=master)](https://travis-ci.org/lunarwings/haps)
Haps [χaps] is a simple DI library, with IoC container included. It is written in pure Python with no external dependencies.

Look how easy it is to use:

```python
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
```

# Installation

    pip install haps

# Documentation

See https://haps.readthedocs.io/en/latest/

# Usage examples

See https://github.com/lunarwings/haps/tree/master/samples

# Testing

Install `requirements.test.txt` and run `py.test` in main directory.

# Changelog

## 1.1.3 (2022-02-04)
- Add `>>` operator
- Add `DI` alias
- Update `.travis.yml`

## 1.1.1 (2018-07-27)
- Fix bug with optional arguments for functions decorated with `@inject`

## 1.1.0 (2018-07-26)
- Add configuration module
- Add application class and runner
- Add profiles
- Minor fixes

## 1.0.5 (2018-07-12)
- `@egg` decorator can be used without function invocation

## 1.0.4 (2018-06-30)
- Add support for python 3.7
- Fix autodiscover sample

## 1.0.0 (2018-06-15)
- First stable release

