import chute
import heapq

class Event(object):
    '''Represents an event in the Discrete Event Simulation.'''
    def __init__(self, time):
        self.time = time
        self.type = 'event'
        self.process = None
        self.events = []

    def __cmp__(self, other):
        return cmp(self.time, other.time)

    def next(self):
        '''
        This will return an Event if there is a follow-up event required. For
        instance, a CreateEvent will always have another CreateEvent after
        a certain interarrival time.
        '''
        # TODO: run the process and add appropriate events
        #       manage this to only generate events as they are needed/appropropriate
        #       (i.e. a hold should only come once a request is fulfilled, same
        #        with a release)
        for event_args in self.process():
            if event_args[0] == chute.request:
                # TODO: what do we use as the requester when the process is just a function?
                # TODO: where to get the args from?
                # TODO: yield chute.request, 'foo'
                # TODO: yield chute.request, 'foo', 'bar'
                heapq.heappush(self.events, RequestEvent(self.time, 'requester', event_args[1:]))

            # TODO: other event types (hold, release)

        while self.events:
            yield heapq.heappop(self.events)


class CreateEvent(Event):
    '''Events for creating new processes.'''
    def __init__(self, when, interarrival, process):
        super(CreateEvent, self).__init__(when)
        self.type = 'create'
        self.process = process
        self.interarrival = interarrival

    def next(self):
        # Register another create after the appropriate interrival time.
        next_create = CreateEvent(
            self.time + self.interarrival(),
            self.interarrival,
            self.process
        )
        heapq.heappush(self.events, next_create)

        for x in super(CreateEvent, self).next():
            yield x

class RequestEvent(Event):
    '''Events for requesting resources. Resources can be anything in Python.'''
    # TODO: clear this out between simulations!
    RESOURCES = {} # resource -> requester using it

    def __init__(self, when, requester, resource):
        super(RequestEvent, self).__init__(when)
        self.type = 'request'
        self.requester = requester
        self.resource = resource

    def __nonzero__(self):
        # TODO: make this inherited? True if the event can be triggered...
        if self.resource not in RequestEvent.RESOURCES:
            RequestEvent.RESOURCES[self.resource] = self.requester
            return True
        else:
            return False
