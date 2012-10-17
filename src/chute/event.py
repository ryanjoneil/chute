import chute
import heapq

class Event(object):
    def __init__(self, clock, event_type, process_name, process_instance):
        self.clock = clock
        self.event_type = event_type
        self.process_name = process_name
        self.process_instance = process_instance

    def __cmp__(self, other):
        return cmp(self.time, other.time)

    def __str__(self):
        return '[%f] %s %d: %s' % (
            self.clock,
            self.process_name,
            self.process_instance,
            self.event_type
        )

class EventGenerator(object):
    def __init__(self,  clock=0):
        self.clock = clock
        self._iter = iter(self)
        self.next()

    def __cmp__(self, other):
        return cmp(self.next(), other.next())

    def next(self):
        return self._iter.next()

    def send(self, *args, **kwds):
        return self._iter.send(*args, **kwds)

class CreateEventGenerator(EventGenerator):
    def __init__(self, process, interarrival, clock=0):
        '''
        A generator of create events. These events add actors to the simulation
        which are modeled by calling either a function or a class.

            - `process`: generator of events that execute the actor's process
            - `interarrival`: lambda that generates interarrival times
            - `clock`: time to start the `CreateGenerator` (default=0)
        '''
        self.process = process # TODO: how should *this* work?
        self.interarrival = interarrival
        self.num = 0
        super(CreateEventGenerator, self).__init__(clock)

    def __iter__(self):
        # Find the first create time.
        next_create = self._generate()
        while True:
            next_clock = yield next_create
            if next_clock is not None and next_clock >= self.clock:
                next_create = self._generate()

    def _generate(self):
        self.clock += self.interarrival()
        e = Event(self.clock, 'create', self.process.__name__, self.num)
        self.num += 1
        return e

#class Event(object):
#    '''Represents an event in the Discrete Event Simulation.'''
#    def __init__(self, time):
#        self.time = time
#        self.type = 'event'
#        self.process = None
#        self.events = []
#
#    def __cmp__(self, other):
#        return cmp(self.time, other.time)
#
#    def next(self):
#        '''
#        This will return an Event if there is a follow-up event required. For
#        instance, a CreateEvent will always have another CreateEvent after
#        a certain interarrival time.
#        '''
#        # TODO: run the process and add appropriate events
#        #       manage this to only generate events as they are needed/appropropriate
#        #       (i.e. a hold should only come once a request is fulfilled, same
#        #        with a release)
#        if callable(self.process):
#            for event_args in self.process():
#                # The three types of requests are: 
#                if event_args[0] == chute.request:
#                    # TODO: what do we use as the requester when the process is just a function?
#                    # TODO: where to get the args from?
#                    # TODO: yield chute.request, 'foo'
#                    # TODO: yield chute.request, 'foo', 'bar'
#                    heapq.heappush(self.events, RequestEvent(self.time, 'requester', event_args[1:]))
#    
#                # TODO: other event types (hold, release)
#                else:
#                    raise NotImplementedError
#
#        while self.events:
#            yield heapq.heappop(self.events)
#
#class CreateEvent(Event):
#    '''Events for creating new processes.'''
#    def __init__(self, when, interarrival, process):
#        super(CreateEvent, self).__init__(when)
#        self.type = 'create'
#        self.process = process
#        self.interarrival = interarrival
#
#    def next(self):
#        # Register another create after the appropriate interrival time.
#        next_create = CreateEvent(
#            self.time + self.interarrival(),
#            self.interarrival,
#            self.process
#        )
#        heapq.heappush(self.events, next_create)
#
#        for x in super(CreateEvent, self).next():
#            yield x
#
#class RequestEvent(Event):
#    '''Events for requesting resources. Resources can be anything in Python.'''
#    # TODO: clear this out between simulations!
#    RESOURCES = {} # resource -> requester using it
#
#    def __init__(self, when, requester, resource):
#        super(RequestEvent, self).__init__(when)
#        self.type = 'request'
#        self.requester = requester
#        self.resource = resource
#
#    def __nonzero__(self):
#        # TODO: make this inherited? True if the event can be triggered...
#        if self.resource not in RequestEvent.RESOURCES:
#            RequestEvent.RESOURCES[self.resource] = self.requester
#            return True
#        else:
#            return False
