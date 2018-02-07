from chaps import Container, Inject
from samples.autodiscover.services.bases import IHeater, IPump


class CoffeeMaker:
    heater: IHeater = Inject()
    pump: IPump = Inject()

    def make_coffee(self):
        return "heater: %r\npump: %r" % (self.heater, self.pump)


Container.autodiscover('samples.autodiscover.services')

if __name__ == '__main__':
    print(CoffeeMaker().make_coffee())
