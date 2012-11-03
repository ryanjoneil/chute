from chute.event import Event
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
        'sent time',         # Time an event is sent to the simulator.
        'start time',        # Time an event starts processing.
        'stop time',         # Time that event stops processing..
        'event type',        # Event type (create, request, etc.).
        'process name',      # Process name (e.g. 'customer')
        'process instance',  # Process instance number (e.g. 5)
        'assigned'           # Resources assigned after the event is fulfilled
                             # (e.g., ['server 1', etc.])
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
        self.assignees = {}
        self.holding = set()

    def _get_resource(self, resource):
        '''
        Converts a resource into the appropriate key. For most resources
        this is just the resource itself. For Events, this is the
        EventGenerator that created it. That way we can have different
        events (RequestEvent, HoldEvent, ReleaseEvent) from the same process
        referencing the same assigned resources.
        '''
        if isinstance(resource, Event):
            return resource.event_gen
        else:
            return resource

    def assign(self, requester, resource):
        '''True if the requested object can be assigned to requester.'''
        requester = self._get_resource(requester)
        resource = self._get_resource(resource)

        # Requesters are not allowed more objects if they are currently
        # assigned as resources to something else.
        if requester in self.assigned:
            return False

        # Objects cannot be assigned if they are currently holding others.
        if resource in self.holding:
            return False

        # Sanity check: assigning something requester already has should
        # always return True.
        try:
            if self.assigned[resource] is requester:
                return True
            return False

        except KeyError:  # Unassigned. Assign to requester.
            self.assigned[resource] = requester
            try:
                self.assignees[requester].add(resource)
            except KeyError:
                self.assignees[requester] = set([resource])
            return True

    def assigned_to(self, requester, resource):
        '''True if the requested object is assigned to requester.'''
        requester = self._get_resource(requester)
        resource = self._get_resource(resource)
        try:
            return self.assigned[resource] is requester
        except KeyError:
            return False

    def hold(self, requester):
        '''True if the requester is allowed to hold objects.'''
        requester = self._get_resource(requester)

        if requester not in self.assigned:
            self.holding.add(requester)
            return True
        return False

    def unhold(self, requester):
        '''Removes a requester from the holding list.'''
        requester = self._get_resource(requester)
        self.holding.discard(requester)

    def resources(self, requester):
        '''Returns the resources assigned to a requester.'''
        try:
            return self.assignees[self._get_resource(requester)]
        except KeyError:
            return set()

    def release(self, requester, resource):
        '''Releases the requested object from requester.'''
        requester = self._get_resource(requester)
        resource = self._get_resource(resource)

        try:
            assert self.assigned[resource] is requester
            del self.assigned[resource]
            self.assignees[requester].discard(resource)
        except:
            return False

        return True

    def run(self, time):
        '''
        Run the simulation until a particular time or until no more events
        are generated, whichever comes first. As events are processed, messages
        are generated in the format specified upon instantiation. Messages
        contain the following fields:

            - sent time:         time an event is sent to the simulator.
            - start time:        time that event starts processing.
            - stop time:         time that event stops processing.
            - event type:        event type (create, request, etc.).
            - process name:      process name (e.g. 'customer')
            - process instance:  process instance number (e.g. 5)
            - assigned:          resources assigned after the event is
                                 fulfilled (e.g., ['server 1', etc.])
        '''
        self.clock = 0
        self.assigned = {}

        # A heap of event generators, prioritized by their next event times.
        heap = []
        for process, interarrival in PROCESSES.items():
            event_gen = CreateEventGenerator(self, process, interarrival)
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

                # The clock should always be the max time we've seen so far.
                event = event_gen.peek
                self.clock = max(self.clock, event.clock)

                # If this event is past our time, stop.
                if self.clock > time:
                    break

                # See if it has an event we can process.
                if event.start(self):
                    # See if it can be processed in its entirety.
                    if not event.stop(self):
                        continue

                    # Take this event off the queue.
                    event_gen.next

                    # Format the assigned list for CSV. For other formats
                    # just use the list of strings we have.
                    alist = self.resources(event)
                    if self.fmt == 'csv':
                        aout = ', '.join(str(x) for x in alist)
                    else:
                        aout = list(map(str, alist))

                    # Generate a DES message.
                    message = {
                        'sent time':        event.sent_time,
                        'start time':       event.start_time,
                        'stop time':        event.stop_time,
                        'event type':       event.event_type,
                        'process name':     event.process_name,
                        'process instance': event.process_instance,
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
                    next_gen = event.spawn()
                    if next_gen is not None:
                        generators.append(next_gen)

                    break

            # If this event is past our time, stop.
            if self.clock > time:
                break

            # Add back all the generators we removed in order to find
            # an event that could be processed.
            while generators:
                heapq.heappush(heap, generators.pop())
