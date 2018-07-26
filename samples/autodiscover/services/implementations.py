from haps import Inject, egg
from samples.autodiscover.services.bases import IHeater, IPump


@egg()
class Heater(IHeater):
    extra_pump: IPump = Inject('extra_pump')

    def heat(self) -> None:
        print("Heating...")

    def __repr__(self):
        return '<Heater id=%s\nextra_pump=%r>' % (id(self), self.extra_pump)


@egg
class Pump(IPump):
    heater: IHeater = Inject()

    def __repr__(self):
        return '<Pump id=%s heater=%r>' % (id(self), self.heater)


@egg(profile='test')
class PumpTest(IPump):
    heater: IHeater = Inject()

    def __repr__(self):
        return '<PumpTest id=%s heater=%r>' % (id(self), self.heater)
