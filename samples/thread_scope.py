from chaps import Container, inject, scope
from chaps.scope.thread import ThreadScope

THREAD_SCOPE = 'thread'  # some unique id


class Worker(object):
    @inject
    def __init__(self, local_data):
        self.local_data = local_data

    def __repr__(self):
        return '<Worker id=%s local_data=%r>' % (id(self), self.local_data)


@scope(THREAD_SCOPE)
class LocalData(object):
    def __repr__(self):
        return '<LocalData id=%s>' % id(self)


Container.configure({
    'local_data': LocalData
})

Container().register_scope(THREAD_SCOPE, ThreadScope)

if __name__ == '__main__':
    import time
    from threading import Thread, RLock

    lock = RLock()

    class MyThread(Thread):
        def run(self):
            for _ in range(3):
                with lock:
                    w = Worker()
                    print('Thread %s -> %r' % (id(self), w))
                time.sleep(0.01)

    threads = [MyThread() for _ in range(3)]
    for t in threads:
        t.start()

    for t in threads:
        t.join()

        # Output
        # Thread 139626471148456 -> <Worker id=139626333099232
        #       local_data=<LocalData id=139626333247024>>
        # Thread 139626333161512 -> <Worker id=139626333247192
        #       local_data=<LocalData id=139626333247304>>
        # Thread 139626333247248 -> <Worker id=139626333247472
        #       local_data=<LocalData id=139626333247584>>
        # Thread 139626471148456 -> <Worker id=139626471640032
        #       local_data=<LocalData id=139626333247024>>
        # Thread 139626333161512 -> <Worker id=139626471147952
        #       local_data=<LocalData id=139626333247304>>
        # Thread 139626333247248 -> <Worker id=139626471148064
        #       local_data=<LocalData id=139626333247584>>
        # Thread 139626471148456 -> <Worker id=139626333247528
        #       local_data=<LocalData id=139626333247024>>
        # Thread 139626333161512 -> <Worker id=139626333247640
        #       local_data=<LocalData id=139626333247304>>
        # Thread 139626333247248 -> <Worker id=139626333247696
        #       local_data=<LocalData id=139626333247584>>
