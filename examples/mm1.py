# A simple M/M/1 Queue example

import chute

@chute.resource
class Server(object):
    pass

server = Server()

@chute.process(chute.dist.exponential(l=0.5)
def customer()
    yield chute.request, server
    yield chute.hold, chute.dist.exponential(l=0.25)
    yield chute.release, server
