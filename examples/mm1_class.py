import chute


@chute.process(chute.dist.exponential(.5))
class Customer(object):
    def __call__(self):
        yield chute.request, 'server'
        yield chute.hold, chute.dist.exponential(.75)
        yield chute.release
