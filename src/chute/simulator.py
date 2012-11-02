from chute import event
from csv import DictWriter
from functools import wraps
import heapq
import json
import os
import sys

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
    MESSAGE_FIELDS = [
        'time sent',         # Time an event is sent to the simulator.
        'time fulfilled',    # Time that event is fulfilled.
        'time waited',       # Time that event spent waiting.
        'event type',        # Event type (create, request, etc.).
        'process name',      # Process name (e.g. 'customer')
        'process instance',  # Process instance number (e.g. 5)
        'objects'            # Objects acted upon (e.g., ['server 1', etc.])
    ]

    def __init__(self, out=sys.stdout, fmt='csv'):
        '''
        Instantiates a simulator. Parameters:

            - out (default=sys.stdout): output file handle
            - fmt (default='csv'): 'csv' or 'json'
        '''
        self.out = out
        self.fmt = fmt

        # TODO: Abstract the message handling component so we can allow
        #       for any format. Provide a Message class and a message hook
        #       so we can also measure things like queue length.
        if fmt == 'csv':
            self.writer = DictWriter(self.out, self.MESSAGE_FIELDS)
            self.writer.writeheader()

    def run(self, time):
        '''
        Run the simulation until a particular time or until no more events
        are generated, whichever comes first. As events are processed, messages
        are generated in the format specified upon instantiation. Messages
        contain the following fields:

            - time sent:         time an event is sent to the simulator.
            - time fulfilled:    time that event is fulfilled.
            - time waited:       time that event spent waiting.
            - event type:        event type (create, request, etc.).
            - process name:      process name (e.g. 'customer')
            - process instance:  process instance number (e.g. 5)
            - objects:           objects acted upon (e.g., ['server 1', etc.])
        '''
        self.clock = 0

        # A heap of event generators, prioritized by their next event times.
        heap = []
        for process, interarrival in PROCESSES.items():
            event_gen = event.CreateEventGenerator(process, interarrival)
            heapq.heappush(heap, event_gen)

        while heap:
            generators = []  # Stack of event generators.

            while True:
                # Get the next event generator off the heap.
                try:
                    event_gen = heapq.heappop(heap)
                except IndexError:
                    break  # Nothing to do. Quit the simulation.

                # Save this to use later.
                generators.append(event_gen)

                # See if it has an event we can process.
                if event_gen.peek.ok(self):
                    next_event = event_gen.next
                    if next_event.clock > self.clock:
                        self.clock = next_event.clock

                    # If this event is past our time, stop.
                    if self.clock > time:
                        break

                    # Generate a DES message.
                    message = {
                        'time sent':        next_event.clock,
                        'time fulfilled':   self.clock,
                        'time waited':      self.clock - next_event.clock,
                        'event type':       next_event.event_type,
                        'process name':     next_event.process_name,
                        'process instance': next_event.process_instance,
                        'objects':          []  # TODO: fill this in
                    }

                    if self.fmt == 'csv':
                        self.writer.writerow(message)
                    elif self.fmt == 'json':
                        self.out.write(json.dumps(message) + os.linesep)

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

            if self.clock > time:
                # Simulation has run to end time.
                break
