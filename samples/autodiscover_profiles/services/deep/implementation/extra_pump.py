from chaps import SINGLETON_SCOPE, dependency, scope
from samples.autodiscover_profiles.services.bases import IPump


@scope(SINGLETON_SCOPE)  # Only one instance is managed for whole application
@dependency(qualifier="extra_pump", profile='!dev')
class ExtraPump(IPump):
    def __repr__(self):
        return '<ExtraPump (not dev) id=%s>' % (id(self),)


@dependency(qualifier="extra_pump", profile='dev')
class ExtraPumpDev(IPump):
    def __repr__(self):
        return '<ExtraPump (dev) id=%s>' % (id(self),)
