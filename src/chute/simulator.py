from chute import event
from functools import wraps
import heapq
from axi.indexer import Indexer

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
            print 'heap =', heap
            generators = []  # Stack of event generators.

            while True:
                # Get the next event generator off the heap.
                try:
                    event_gen = heapq.heappop(heap)
                    print 'event_gen', event_gen, 'peek =', event_gen.peek
                except IndexError:
                    raise
                    break  # Nothing to do. Quit the simulation.

                # Save this to use later.
                generators.append(event_gen)

                # See if it has an event we can process.
                if event_gen.peek.ok(clock):
                    next_event = event_gen.next
                    clock = next_event.clock
                    print 'next_event', next_event

                    # If the generator is done, take it off our list.
                    if event_gen.done:
                        generators.pop()

                    # See if this event spawns a new event generator.
                    next_gen = next_event.spawn()
                    if next_gen is not None:
                        generators.append(next_gen)

                    break

            # Add back all the generators we removed in order to find
            # an event that could be processed.
            while generators:
                heapq.heappush(heap, generators.pop())

            if clock >= time:
                # Simulation has run to end time.
                print 'quit'
                break
