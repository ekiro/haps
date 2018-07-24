from haps import inject
from haps.application import Application, ApplicationRunner
from haps.config import Config, Configuration
from samples.autodiscover.services.bases import IHeater


@Configuration.resolver('heat_count')
def _():
    return 5


Configuration.env_resolver('config_var')
Configuration.set('another_var', 10)


class MyApp(Application):
    config_var: str = Config()
    count: int = Config('heat_count')
    another_var: int = Config()

    @inject
    def __init__(self, heater: IHeater):
        self.heater = heater

    def run(self):
        for _ in range(self.count):
            self.heater.heat()
        print(self.config_var, self.another_var)


if __name__ == '__main__':
    ApplicationRunner.run(MyApp, module_paths=[
        'autodiscover.services'
    ])
