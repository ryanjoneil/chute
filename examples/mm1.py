# A simple M/M/1 Queue example

import chute
#import random

#@chute.process(lambda: random.expovariate(1))
@chute.process
def customer():
    yield chute.request, 'server 1'
    yield chute.hold, chute.dist.exponential(0.25)
    yield chute.release, 'server 1'

if __name__ == '__main__':
    s = chute.Simulator()
    s.run(10)
