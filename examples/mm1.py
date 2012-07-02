# A simple M/M/1 Queue example

import chute

@chute.process(chute.dist.exponential(1))
def customer():
    yield chute.request, 'server 1'
    yield chute.hold, chute.dist.exponential(0.25)
    yield chute.release, 'server 1'

@chute.process(chute.dist.exponential(1))
class Customer(object):
    NUM = 1

    def __init__(self):
        self.num = Customer.NUM
        Customer.NUM += 1

    def __repr__(self):
        return 'customer %d' % self.num

    def __call__(self):
        yield chute.request, 'server 1'
        yield chute.hold, chute.dist.exponential(0.25)
        yield chute.release, 'server 1'

if __name__ == '__main__':
    s = chute.Simulator()
    s.run(10)
