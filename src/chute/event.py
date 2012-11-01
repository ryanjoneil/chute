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

    def ok(self, clock):
        '''Returns True if the event can be processed, False otherwise.'''
        return True  # TODO: deal with request, etc.


class EventGenerator(object):
    def __init__(self, clock=0):
        self.clock = clock
        self._iter = iter(self)
        self._next = None
        self._done = False
        self.peek

    def __cmp__(self, other):
        return cmp(self.peek, other.peek)

    @property
    def done(self):
        return self._done

    @property
    def peek(self):
        if self._next is None:
            self._next = self._iter.next()
        return self._next

    @property
    def next(self):
        n = self._next
        try:
            self._next = self._iter.next()
        except StopIteration:
            self._next = None
            self._done = True
        return n


class CreateEventGenerator(EventGenerator):
    def __init__(self, process, interarrival, clock=0):
        '''
        A generator of create events. These events add actors to the simulation
        which are modeled by calling either a function or a class.

            - process: generator of events that execute the actor's process
            - interarrival: lambda that generates interarrival times
            - clock: time to start the CreateGenerator (default=0)
        '''
        self.process = process
        self.interarrival = interarrival
        self.num = 0
        super(CreateEventGenerator, self).__init__(clock)

    def __iter__(self):
        while True:
            self.clock += self.interarrival()
            e = Event(self.clock, 'create', self.process, self.num)
            self.num += 1
            yield e

    def __repr__(self):
        return 'CREATE'


class ProcessEventGenerator(EventGenerator):
    def __init__(self, create_event):
        '''
        A generator of events for a process running in the system. This
        generator is built once a 'create' Event has been constructed.

            - create_event: Event that instantiated the actor
        '''
        self.create_event = create_event
        if isinstance(create_event.process, type):
            self._process = iter(create_event.process()())
        else:
            self._process = iter(create_event.process())
        super(ProcessEventGenerator, self).__init__(create_event.clock)

    def __iter__(self):
        for args in self._process.next():
            e = Event(
                self.clock,
                args[0],
                self.create_event.process,
                self.create_event.process_instance
            )
            yield e

    def __repr__(self):
        return 'PROCESS %s' % (self.create_event.process_instance)
