from chaps.scope import Scope


class InstanceScope(Scope):
    def get_object(self, class_):
        return class_()
