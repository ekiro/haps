from haps import SINGLETON_SCOPE, Container, Egg, inject, scope


class HeaterInterface:
    pass


class PumpInterface:
    pass


class ExtraPumpInterface(PumpInterface):
    pass


class CoffeeMaker:
    @inject
    def __init__(self, heater: HeaterInterface, pump: PumpInterface):
        self.heater = heater
        self.pump = pump

    def make_coffee(self):
        return "heater: %r\npump: %r" % (self.heater, self.pump)


class Heater:
    @inject
    def __init__(self, extra_pump: ExtraPumpInterface):
        self.extra_pump = extra_pump

    def __repr__(self):
        return '<Heater id=%s\nextra_pump=%r>' % (
            id(self), self.extra_pump)


class Pump:
    @inject
    def __init__(self, heater: HeaterInterface):
        self.heater = heater

    def __repr__(self):
        return '<Pump id=%s heater=%r>' % (id(self), self.heater)


@scope(SINGLETON_SCOPE)  # Only one instance per application is allowed
class ExtraPump:
    def __repr__(self):
        return '<ExtraPump id=%s>' % (id(self),)


Container.configure([
    Egg(HeaterInterface, HeaterInterface, None, Heater),
    Egg(PumpInterface, PumpInterface, None, Pump),
    Egg(ExtraPumpInterface, ExtraPumpInterface, None, ExtraPump),
])

if __name__ == '__main__':
    print(CoffeeMaker().make_coffee())

    # Ouput
    # heater: <Heater id=140440945316584
    # extra_pump=<ExtraPump id=140440945316696>>
    # pump: <Pump id=140440945316640 heater=<Heater id=140440945316808
    # extra_pump=<ExtraPump id=140440945316696>>>
