from chaps.scope import Scope


class InstanceScope(Scope):
    def get_object(self, egg_):
        return egg_()
