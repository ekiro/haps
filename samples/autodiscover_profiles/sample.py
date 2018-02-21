from chaps import Container, Inject, inject
from samples.autodiscover_profiles.services.bases import IHeater, IPump


class CoffeeMaker:
    heater: IHeater = Inject()

    @inject
    def __init__(self, pump: IPump):
        self.pump = pump

    def make_coffee(self):
        return "heater: %r\npump: %r" % (self.heater, self.pump)


if __name__ == '__main__':
    print("Dev profile")
    Container.autodiscover('samples.autodiscover_profiles.services',
                           profiles={'dev'})
    print(CoffeeMaker().make_coffee())

    Container._reset()
    print("\nNot dev profile")
    Container.autodiscover('samples.autodiscover_profiles.services',
                           profiles={'production'})
    print(CoffeeMaker().make_coffee())
