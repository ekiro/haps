from chaps.scope import Scope


class SingletonScope(Scope):
    _objects = {}

    def get_object(self, class_):
        if class_ in self._objects:
            return self._objects[class_]
        else:
            obj = class_()
            self._objects[class_] = obj
            return obj
