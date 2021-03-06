import chute

@chute.process(chute.dist.exponential(.5))
def customer():
    yield chute.request, 'server'
    yield chute.hold, chute.dist.exponential(.75)
    yield chute.release
    