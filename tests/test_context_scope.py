import queue
import threading

from haps.scopes.context import ContextScope


def test_get_object(some_class):
    @ContextScope.with_context
    def t():
        return ContextScope().get_object(some_class)

    some_instance = t()
    assert isinstance(some_instance, some_class)


def test_get_multiple_objects_threaded(some_class):
    q = queue.Queue()

    scope = ContextScope()

    class MyThread(threading.Thread):
        @ContextScope.with_context
        def run(self):
            for _ in range(100):
                q.put(scope.get_object(some_class))

    threads = {MyThread() for _ in range(10)}
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    objects = [q.get_nowait() for _ in range(1000)]

    assert all(isinstance(o, some_class) for o in objects)
    assert len({id(o) for o in objects}) == 10


def test_multiple_objects_from_different_contexts(some_class):
    objects = []

    scope = ContextScope()

    @ContextScope.with_context
    def get_obj():
        o1 = scope.get_object(some_class)
        o2 = scope.get_object(some_class)
        return o1, o2

    for _ in range(100):
        objects.extend(get_obj())

    assert all(isinstance(o, some_class) for o in objects)
    assert len(objects) == 200
    assert len({id(o) for o in objects}) == 100
