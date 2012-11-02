from chute.event_gen import CreateEventGenerator
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
        'assigned'           # Objects assigned (e.g., ['server 1', etc.])
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

        self.clock = 0
        self.assigned = {}
        self.holding = set()

    def assign(self, requester, requested):
        '''True if the requested object can be assigned to requester.'''
        # TODO: deal with logic where one process is requesting another

        # Requesters are not allowed more objects if they are currently
        # assigned as resources to something else.
        if requester in self.assigned:
            return False

        # Objects cannot be assigned if they are currently holding others.
        if requested in self.holding:
            return False

        # Sanity check: assigning something requester already has should
        # always return True.
        try:
            if self.assigned[requested] is requester:
                return True
            return False
        except KeyError:  # Unassigned. Assign to requester.
            self.assigned[requested] = requester
            return True

    def hold(self, requester):
        '''True if the requester is allowed to hold objects.'''
        if requester not in self.assigned and requester not in self.holding:
            self.holding.add(requester)
            return True
        return False

    def release(self, requester):
        '''Releases the requested object from requester.'''
        # TODO: make this better.
        for key, val in self.assigned.items():
            if val is requester:
                del self.assigned[key]
        return True

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
            - assigned:          objects assigned (e.g., ['server 1', etc.])
        '''
        self.clock = 0
        self.assigned = {}

        # A heap of event generators, prioritized by their next event times.
        heap = []
        for process, interarrival in PROCESSES.items():
            event_gen = CreateEventGenerator(process, interarrival)
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

                    # Format the assigned list for CSV. For other formats
                    # just use the list of strings we have.
                    if self.fmt == 'csv':
                        aout = ', '.join(str(x) for x in next_event.assigned)
                    else:
                        aout = list(map(str, next_event.assigned))

                    # Generate a DES message.
                    message = {
                        'time sent':        next_event.clock,
                        'time fulfilled':   self.clock,
                        'time waited':      self.clock - next_event.clock,
                        'event type':       next_event.event_type,
                        'process name':     next_event.process_name,
                        'process instance': next_event.process_instance,
                        'assigned':         aout
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
