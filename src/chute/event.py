class Event(object):
    '''Represents an event in the Discrete Event Simulation.'''
    def __init__(self, time):
        self.time = time
        self.type = 'event'
        self.process = None

    def __cmp__(self, other):
        return cmp(self.time, other.time)

class CreateEvent(Event):
    '''Events for creating new processes.'''
    def __init__(self, time, process):
        super(CreateEvent, self).__init__(time)
        self.type = 'create'
        self.process = process
