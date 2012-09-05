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
        while self.events:
            yield heapq.heappop(self.events)
        # TODO: run the process and add appropriate events

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
