# A simple M/M/1 Queue example

import chute
import random

random.seed(0)

# A process is anything that is callable. And a resource can be anything
# that is hashable by Python, so really anything at all:
@chute.process(chute.dist.exponential(1))
#@chute.process(lambda: 1)
def customer():
    yield chute.request, 'server 1'
    #yield chute.request, 'server 2'
    #yield chute.hold(chute.dist.exponential(0.25))
    #yield chute.release('server 1')

# Here is an equivalent process, from the perspective of chute:
#@chute.process(chute.dist.exponential(1))
#@chute.process(lambda: 1)
class Customer(object):
    def __call__(self):
        yield chute.request, 'server 1'
        yield chute.hold, chute.dist.exponential(0.25)
        yield chute.release, 'server 1'

# Simulator objects can be created manually as below, or will available
# with normal defaults using the chute command:
if __name__ == '__main__':
    s = chute.Simulator()
    s.run(4)
