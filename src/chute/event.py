class Event(object):
    '''Represents an event in the Discrete Event Simulation.'''
    def __init__(self, time):
        self.time = time
        self.type = 'event'
        self.process = None

    def __cmp__(self, other):
        return cmp(self.time, other.time)

    def next(self):
        '''
        This will return an Event if there is a follow-up event required. For
        instance, a CreateEvent will always have another CreateEvent after
        a certain interarrival time.
        '''
        return None


class CreateEvent(Event):
    '''Events for creating new processes.'''
    def __init__(self, when, interarrival, process):
        super(CreateEvent, self).__init__(when)
        self.type = 'create'
        self.process = process
        self.interarrival = interarrival

    def next(self):
        # Register another create after the appropriate interrival time.
        when = self.time + self.interarrival()
        return CreateEvent(when, self.interarrival, self.process)
