from threading import local

from chaps.scope import Scope


class ThreadScope(Scope):
    _thread_local = local()

    def get_object(self, class_):
        try:
            objects = self._thread_local.objects
        except AttributeError:
            objects = {}
            self._thread_local.objects = objects

        if class_ in objects:
            return objects[class_]
        else:
            obj = class_()
            objects[class_] = obj
            return obj
