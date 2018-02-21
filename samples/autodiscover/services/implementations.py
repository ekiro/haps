from chaps import Inject, dependency
from samples.autodiscover.services.bases import IHeater, IPump


@dependency
class Heater(IHeater):
    extra_pump: IPump = Inject('extra_pump')

    def heat(self) -> None:
        print("Heating...")

    def __repr__(self):
        return '<Heater id=%s\nextra_pump=%r>' % (
            id(self), self.extra_pump)


@dependency
class Pump(IPump):
    heater: IHeater = Inject()

    def __repr__(self):
        return '<Pump id=%s heater=%r>' % (id(self), self.heater)
