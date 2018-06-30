from haps import Container, Inject, inject
from samples.autodiscover.services.bases import IHeater, IPump


class CoffeeMaker:
    heater: IHeater = Inject()

    @inject
    def __init__(self, pump: IPump):
        self.pump = pump

    def make_coffee(self):
        return "heater: %r\npump: %r" % (self.heater, self.pump)


if __name__ == '__main__':
    Container.autodiscover(['samples.autodiscover.services'])
    print(CoffeeMaker().make_coffee())
