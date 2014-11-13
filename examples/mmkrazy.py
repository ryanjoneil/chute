import chute
import random

NUM_SERVERS = 4
SERVERS = ['server %d' % i for i in range(NUM_SERVERS)]

@chute.process(chute.dist.exponential(.5))
class Customer(object):
    ACTIVE = set()

    def __call__(self):
        # Track existing customers so we can randomly use them as resources.
        self.ACTIVE.add(self)

        if random.random() < .1:
            # Most customers just require one server.
            yield chute.request, SERVERS
            yield chute.hold, chute.dist.exponential(.75)

        else:
            # A particularly difficult customer will do all of the following:
            #     - Use the time of 2 servers.
            #     - Ask for the manager.
            #     - Release a server and the manager, but involve a customer.
            yield chute.request, SERVERS, SERVERS
            yield chute.hold, chute.dist.exponential(.5)
            yield chute.request, 'manager'
            yield chute.hold, chute.dist.exponential(.75)
            yield chute.release, SERVERS, 'manager'

            # If there are any other customers around, get their time too.
            others = self.ACTIVE.difference(set([self]))
            if others:
                yield chute.request, list(others)
                yield chute.hold, chute.dist.exponential(.65)

        yield chute.release
        self.ACTIVE.remove(self)
