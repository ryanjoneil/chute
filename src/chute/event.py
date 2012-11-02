class Event(object):
    def __init__(self, event_type, clock, process, process_instance):
        self.event_type = event_type
        self.clock = clock
        self.process = process
        self.process_name = process.__name__
        self.process_instance = process_instance
        self.assigned = []

    def __str__(self):
        return '[%f] %s %d: %s' % (
            self.clock,
            self.process_name,
            self.process_instance,
            self.event_type
        )

    def __lt__(self, other):
        return self.clock < other.clock

    def spawn(self):
        '''Either spawns a new event generator, or returns None.'''
        return None

    def ok(self, simulator):
        '''Returns True if the event can be processed, False otherwise.'''
        return True


class CreateEvent(Event):
    '''
    Represents an event that spawns a process. Creates are generated by
    chute using the @chute.process decorator. For example, a simple M/M/1
    queue with multiple customers and a single server may be modeled as:

        import chute

        @chute.process(chute.dist.exponential(1))
        def customer():
            yield chute.request, 'server'
            yield chute.hold, chute.dist.exponential(0.25)
            yield chute.release
    '''
    EVENT_TYPE = 'create'

    def __init__(self, *args):
        super(CreateEvent, self).__init__(CreateEvent.EVENT_TYPE, *args)

    def spawn(self):
        from chute.event_gen import ProcessEventGenerator
        return ProcessEventGenerator(self)


class RequestEvent(Event):
    '''
    Represents an event that requests a single resource or set of resources.
    The requesting process will wait until every resource it needs is
    available and assigned to it before proceeding. Requests can be made for
    anything in Python. For instance, this request waits for the single
    string 'server':

        @chute.process(chute.dist.exponential(1)):
        def customer():
            yield chute.request, 'server'

    One could just as easily request the number 5, or any class instance:

            yield chute.request, 5
            yield chute.request, bar

    This requests two objects, waiting for both of them. It does not matter
    in which order they are obtained:

            yield chute.request, 'server 1', 'server 2'

    This requests and waits for 'server 1', then requests and waits for
    'server 2':

            yield chute.request, 'server 1'
            yield chute.request, 'server 2'

    Requests can also be make for one of any number of objects. For instance,
    if we had a list of ten servers and we didn't care which one we got:

            servers = ['server %d' % i for i in range(10)]
            yield chute.request, servers

    If we wanted any one of the servers and the manager:

            yield chute.request, servers, 'manager'

    Or if we wanted any two of the servers and we didn't care which, so
    long as we bothered the manager with them:

            yield chute.request, servers, servers, 'manager'
    '''
    EVENT_TYPE = 'request'

    def __init__(self, *args, **kwds):
        super(RequestEvent, self).__init__(RequestEvent.EVENT_TYPE, *args)
        self.event_args = kwds['event_args']

        # Convert each sequence of requested objects to a tuple, and
        # store it as unassigned. Once requested objects as assigned,
        # they go into the assigned set.
        self.unassigned = set()
        for e in self.event_args:
            if type(e) not in (list, tuple):
                e = (e,)
            self.unassigned.add(tuple(e))

    def ok(self, simulator):
        '''Assigns any requested objects that can be to the process.'''
        is_ok = True

        # Try and assign as much as possible of what is requested.
        for request_options in list(self.unassigned):
            is_assigned = False
            for option in request_options:
                # Try to get this object from the simulator.
                if simulator.assign(self, option):
                    self.unassigned.remove(request_options)
                    self.assigned.append(option)
                    is_assigned = True
                    break

            # Allow is_ok to go to False, but keep trying to assing objects.
            is_ok = is_ok and is_assigned

        return is_ok
