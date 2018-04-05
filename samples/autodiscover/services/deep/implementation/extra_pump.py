from chaps import SINGLETON_SCOPE, egg, scope, Inject, inject
from samples.autodiscover.services.bases import IPump, IHeater


class HelpingPump(IPump):
    def __init__(self, heater: IHeater):
        self.heater = heater

    def __repr__(self):
        return f'<HelpingPump id={id(self)}\nheater={id(self.heater)}'


@scope(SINGLETON_SCOPE)
@egg(qualifier="extra_pump")
class ExtraPump(IPump):
    helper: IPump = Inject('helping_pump')

    @staticmethod
    @egg(qualifier="helping_pump")
    @inject
    def helper_factory(heater: IHeater) -> IPump:
        ret = HelpingPump(heater)
        # some actions
        return ret

    def __repr__(self):
        return (f'<ExtraPump (not dev) id={id(self)}\n'
                f'helper={repr(self.helper)}>')
