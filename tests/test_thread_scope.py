try:
    import queue
except ImportError:
    import Queue as queue  # python2

import threading

from haps.scopes.thread import ThreadScope


def test_get_object(some_class):
    some_instance = ThreadScope().get_object(some_class)
    assert isinstance(some_instance, some_class)


def test_get_multiple_objects(some_class):
    q = queue.Queue()

    class MyThread(threading.Thread):
        def run(self):
            scope = ThreadScope()
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
