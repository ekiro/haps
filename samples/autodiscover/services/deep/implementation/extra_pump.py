from chaps import SINGLETON_SCOPE, scope, service
from samples.autodiscover.services.bases import IPump


@scope(SINGLETON_SCOPE)  # Only one instance is managed for whole application
@service(qualifier="extra_pump")
class ExtraPump(IPump):
    def __repr__(self):
        return '<ExtraPump id=%s>' % (id(self),)
