import chute
import heapq

class Event(object):
    def __init__(self, clock, event_type, process, process_instance):
        self.clock = clock
        self.event_type = event_type
        self.process = process
        self.process_name = process.__name__
        self.process_instance = process_instance

    def __str__(self):
        return '[%f] %s %d: %s' % (
            self.clock,
            self.process_name,
            self.process_instance,
            self.event_type
        )

    def __cmp__(self, other):
        return cmp(self.clock, other.clock)

    def spawn(self):
        '''Either spawns a new event generator, or returns None.'''
        if self.event_type == 'create':
            return ProcessEventGenerator(self)

        return None


class EventGenerator(object):
    def __init__(self,  clock=0):
        self.clock = clock
        self._iter = iter(self)
        self.next()

    def __cmp__(self, other):
        return cmp(self.next(), other.next())

    def __iter__(self):
        # Get the first event
        next_event = self._generate()
        while True:
            next_clock = yield next_event
            if next_event is not None and next_clock >= self.clock:
                next_event = self._generate()

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

    def _generate(self):
        self.clock += self.interarrival()
        e = Event(self.clock, 'create', self.process, self.num)
        self.num += 1
        return e

class ProcessEventGenerator(EventGenerator):
    def __init__(self, create_event):
        '''
        A generator of events for a process running in the system. This
        generator is built once a 'create' `Event` has been consrtucted.

            - `create_event`: ` Event` that instantiated the actor
        '''
        self.create_event = create_event
        self._process = iter(create_event.process())
        super(ProcessEventGenerator, self).__init__(create_event.clock)

    def _generate(self):
        args = self._process.next()
        e = Event(
            self.clock,
            args[0],
            self.create_event.process,
            self.create_event.process_instance
        )
        self.clock += 1
        return e
