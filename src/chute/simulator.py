from chute import event
from functools import wraps
import heapq

PROCESSES = {}

# TODO: This needs to use the decorator util library, but I can't remember
#       exactly how that works without the documentation at hand...
def process(interarrival):
    '''
    Registers a process with the simulator. A process can be anything that is
    callable and is a generator, including classes that implement __call__.
    When a process is instantiated, the simulator will call it and expect it
    to start yielding simulation events.

    Note: if the process is just a generator, it should be able to be invoked
    multiple times within the same thread without damaging its state.

    interarrival can be either a number representing the interarrival time
    between creating new instances of the process or a function that returns
    the next interarrival time.
    '''
    def decorator(p):
        # If interarrival is not callable, turn it into a function that is.
        if callable(interarrival):
            PROCESSES[p] = interarrival
        else:
            PROCESSES[p] = lambda: interarrival

        @wraps
        def wrapper(*args, **kwds):
            return p(*args, **kwds)
        return wrapper

    return decorator

class Simulator(object):
    def run(self, time):
        '''Run the simulation until a particular time.'''
        self.clock = 0

        # Make a copy of registered processes just in case it changes.
        self.processes = PROCESSES.copy()

        # Initiate a new event priority queue and add an event for the first
        # instantiation of each process type to it.
        self.heap = []
        for process, interarrival in self.processes.items():
            when = interarrival()
            heapq.heappush(self.heap,
                event.CreateEvent(when, interarrival, process)
            )

        # Run the DES algorithm until we are either out of events entirely or
        # the allotted time has passed (we get an event > time).
        while self.heap:
            next_event = heapq.heappop(self.heap)
            if next_event.time > time:
                break

            # TODO: registration of event receivers and formatting
            print next_event.process, next_event.type, next_event.time

            # Current time = the time of our current event.
            self.clock = next_event.time

            # See if this event triggers another event.
            followup_event = next_event.next()
            if followup_event is not None:
                heapq.heappush(self.heap, followup_event)
