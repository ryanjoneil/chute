# A simple M/M/1 Queue example using a function.

import chute

# A process is anything that is callable. And a resource can be anything
# that is hashable by Python, so really anything at all:
@chute.process(chute.dist.exponential(1))
def customer():
    yield chute.request, ['server 1', 'server 2'], 'manager'
    #yield chute.request, 'server 2'
    # yield chute.hold(chute.dist.exponential(0.25))
    # yield chute.release('server 1')
