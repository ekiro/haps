from chaps import SINGLETON_SCOPE, dependency, scope
from samples.autodiscover.services.bases import IPump


@scope(SINGLETON_SCOPE)  # Only one instance is managed for whole application
@dependency(qualifier="extra_pump")
class ExtraPump(IPump):
    def __repr__(self):
        return '<ExtraPump id=%s>' % (id(self),)
