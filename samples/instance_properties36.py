from chaps import SINGLETON_SCOPE, Container, Inject, scope


class HeaterInterface:
    pass


class PumpInterface:
    pass


class ExtraPumpInterface(PumpInterface):
    pass


class CoffeeMaker(object):
    heater: HeaterInterface = Inject()
    pump: PumpInterface = Inject()

    def make_coffee(self):
        return "heater: %r\npump: %r" % (self.heater, self.pump)


class Heater(HeaterInterface):
    amazing_pump: ExtraPumpInterface = Inject()

    def __repr__(self):
        return '<Heater id=%s\namazing_pump=%r>' % (
            id(self), self.amazing_pump)


class Pump(PumpInterface):
    heater: HeaterInterface = Inject()

    def __repr__(self):
        return '<Pump id=%s heater=%r>' % (id(self), self.heater)


@scope(SINGLETON_SCOPE)  # Only one instance is managed for whole application
class ExtraPump(ExtraPumpInterface):
    def __repr__(self):
        return '<ExtraPump id=%s>' % (id(self),)


Container.configure({
    HeaterInterface: Heater,
    PumpInterface: Pump,
    ExtraPumpInterface: ExtraPump
})

if __name__ == '__main__':
    print(CoffeeMaker().make_coffee())

    # Ouput
    # heater: <Heater id=140440945316584
    # amazing_pump=<ExtraPump id=140440945316696>>
    # pump: <Pump id=140440945316640 heater=<Heater id=140440945316808
    # amazing_pump=<ExtraPump id=140440945316696>>>
