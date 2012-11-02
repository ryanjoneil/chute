class Event(object):
    def __init__(self, event_type, clock, process, process_instance):
        self.event_type = event_type
        self.clock = clock
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

    def __lt__(self, other):
        return self.clock < other.clock

    def spawn(self):
        '''Either spawns a new event generator, or returns None.'''
        return None

    def ok(self, simulator):
        '''Returns True if the event can be processed, False otherwise.'''
        return True


class CreateEvent(Event):
    '''Represents an event that spawns a process.'''
    EVENT_TYPE = 'create'

    def __init__(self, *args):
        super(CreateEvent, self).__init__(CreateEvent.EVENT_TYPE, *args)

    def spawn(self):
        from chute.event_gen import ProcessEventGenerator
        return ProcessEventGenerator(self)


class RequestEvent(Event):
    '''Represents an event that spawns a process.'''
    EVENT_TYPE = 'request'

    def __init__(self, *args):
        super(RequestEvent, self).__init__(RequestEvent.EVENT_TYPE, *args)

    def ok(self, simulator):
        return False
