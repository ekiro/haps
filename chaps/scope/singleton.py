from chaps.scope import Scope


class SingletonScope(Scope):
    _objects = {}

    def get_object(self, egg_):
        if egg_ in self._objects:
            return self._objects[egg_]
        else:
            obj = egg_()
            self._objects[egg_] = obj
            return obj
