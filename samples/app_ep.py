from haps import inject
from haps.application import Application, ApplicationRunner
from samples.autodiscover.services.bases import IHeater


class MyApp(Application):
    @inject
    def __init__(self, heater: IHeater):
        self.heater = heater

    def run(self):
        self.heater.heat()


if __name__ == '__main__':
    ApplicationRunner.run(MyApp, module_paths=[
        'autodiscover.services'
    ])
