import chute

NUM_SERVERS = 2
servers = ['server %d' % i for i in range(NUM_SERVERS)]

@chute.process(chute.dist.exponential(.5))
def customer():
    yield chute.request, servers
    yield chute.hold, chute.dist.exponential(.75)
    yield chute.release
    