from chaps import Container, Inject, inject
from samples.autodiscover.services.bases import IHeater, IPump


class CoffeeMaker:
    heater: IHeater = Inject()

    @inject
    def __init__(self, pump: IPump):
        self.pump = pump

    def make_coffee(self):
        return "heater: %r\npump: %r" % (self.heater, self.pump)


Container.autodiscover('samples.autodiscover.services')

if __name__ == '__main__':
    print(CoffeeMaker().make_coffee())
