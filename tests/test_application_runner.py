from haps import Inject
from haps.application import Application, ApplicationRunner


def test_application():
    class App(Application):
        ran = False

        def run(self) -> None:
            App.ran = True

    ApplicationRunner.run(App)
    assert App.ran


def test_application_with_autodiscovery():
    from samples.autodiscover.sample import (IPump, IHeater)

    class App(Application):
        ran = False
        pump: IPump = Inject()
        heater: IHeater = Inject()

        def run(self) -> None:
            assert isinstance(self.pump, IPump)
            assert isinstance(self.heater, IHeater)
            App.ran = True

    ApplicationRunner.run(
        App, extra_module_paths=['samples.autodiscover.services'])
    assert App.ran
