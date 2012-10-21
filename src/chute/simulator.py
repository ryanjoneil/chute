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
        clock = 0

        # A heap of event generators, prioritized by their next event times.
        heap = []
        for process, interarrival in PROCESSES.items():
            event_gen = event.CreateEventGenerator(process, interarrival)
            heapq.heappush(heap, event_gen)

        while heap:
            print '\n', clock, heap
            event_gen = heapq.heappop(heap)
            try:
                print 'SIM CLOCK = ', clock, event_gen
                next_event = event_gen.send(clock)
            except StopIteration:
                print 'SIM STOP PROCESS', event_gen
                # This event generator is done. Abandon it.
                continue

            clock = next_event.clock

            # See if this event spawns a new event generator.
            next_gen = next_event.spawn()
            if next_gen is not None:
                print 'SIM ADD PROCESS', next_gen
                heapq.heappush(heap, next_gen)

            print 'SIM RE-ADD PROCESS', event_gen
            heapq.heappush(heap, event_gen)

            print 'SIM NEXT EVENT', next_event

            if clock >= time:
                # Stop the simulation when we reach our end time.
                break

