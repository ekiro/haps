from chaps import Container, inject


class Obj(object):
    @inject
    def __init__(self, my_obj):
        pass

    def __repr__(self):
        return '<Obj id=%s \n  my_obj=%r>' % (id(self), self.my_obj)


class SomeComplexObject(object):
    def __init__(self, x):
        self.x = x

    def __repr__(self):
        return '<SomeComplexObject id=%s, x=%s>' % (id(self), self.x)


def create_my_obj():
    import time
    return SomeComplexObject(time.time())


Container.configure({
    'my_obj': create_my_obj
})

if __name__ == '__main__':
    objs = {Obj() for _ in range(5)}
    for obj in objs:
        print(obj)

    # Ouput
    # <Obj id=139825808224552
    #   my_obj=<SomeComplexObject id=139825802697528, x=1493196517.097129>>
    # <Obj id=139825802697584
    #   my_obj=<SomeComplexObject id=139825802697752, x=1493196517.0971444>>
    # <Obj id=139825808225224
    #   my_obj=<SomeComplexObject id=139825802696128, x=1493196517.0971143>>
    # <Obj id=139825802697696
    #   my_obj=<SomeComplexObject id=139825802697864, x=1493196517.0971515>>
    # <Obj id=139825802696184
    #   my_obj=<SomeComplexObject id=139825802697640, x=1493196517.0971372>>
