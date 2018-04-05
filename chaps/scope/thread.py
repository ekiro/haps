from threading import local

from chaps.scope import Scope


class ThreadScope(Scope):
    _thread_local = local()

    def get_object(self, egg_):
        try:
            objects = self._thread_local.objects
        except AttributeError:
            objects = {}
            self._thread_local.objects = objects

        if egg_ in objects:
            return objects[egg_]
        else:
            obj = egg_()
            objects[egg_] = obj
            return obj
