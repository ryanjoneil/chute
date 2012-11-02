# A simple M/M/1 Queue example using a class.

import chute

@chute.process(chute.dist.exponential(1))
class Customer(object):
    def __call__(self):
        yield chute.request, 'server 1'
        # yield chute.hold, chute.dist.exponential(0.25)
        # yield chute.release, 'server 1'
