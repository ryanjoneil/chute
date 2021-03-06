class Event(object):
    def __init__(self, event_type, event_gen, clock, process, process_inst):
        self.event_type = event_type
        self.event_gen = event_gen  # Event generator.
        self.clock = clock
        self.process = process
        self.process_name = process.__name__
        self.process_instance = process_inst

        self.assigned = []  # Resources assigned to a process.

        self.sent_time = self.clock
        self.start_time = None
        self.stop_time = None

    def __str__(self):
        return '[%f] %s %d: %s' % (
            self.clock,
            self.process_name,
            self.process_instance,
            self.event_type
        )

    def __lt__(self, other):
        # In the unlikely chance that two requests are at the same time,
        # HoldRequest instances should always come first. This is to avoid
        # requestors being assigned when they are trying to hold resources.
        if self.clock == other.clock:
            if isinstance(self, HoldEvent):
                return True
            elif isinstance(other, HoldEvent):
                return False

        return self.clock < other.clock

    def spawn(self):
        '''Either spawns a new event generator, or returns None.'''
        return None

    def start(self, simulator):
        '''Returns True if the event can be processed, False otherwise.'''
        if not simulator.clock < self.clock:
            if self.start_time is None:
                self.start_time = simulator.clock
            return True
        return False

    def stop(self, simulator):
        '''Returns True if the event is processed, False otherwise.'''
        if not simulator.clock < self.clock:
            if self.stop_time is None:
                self.stop_time = simulator.clock
            return True
        return False


class CreateEvent(Event):
    '''
    Represents an event that spawns a process. Creates are generated by
    chute using the @chute.process decorator. For example, a simple M/M/1
    queue with multiple customers and a single server may be modeled as:

        import chute

        @chute.process(chute.dist.exponential(1))
        def customer():
            yield chute.request, 'server'
            yield chute.hold, chute.dist.exponential(0.25)
            yield chute.release
    '''
    EVENT_TYPE = 'create'

    def __init__(self, *args):
        super(CreateEvent, self).__init__(CreateEvent.EVENT_TYPE, *args)

    def spawn(self):
        from chute.event_gen import ProcessEventGenerator
        return ProcessEventGenerator(self.event_gen.simulator, self)


class RequestEvent(Event):
    '''
    Represents an event that requests a single resource or set of resources.
    The requesting process will wait until every resource it needs is
    available and assigned to it before proceeding. Requests can be made for
    anything in Python. For instance, this request waits for the single
    string 'server':

        @chute.process(chute.dist.exponential(1)):
        def customer():
            yield chute.request, 'server'

    One could just as easily request the number 5, or any class instance:

            yield chute.request, 5
            yield chute.request, bar

    This requests two objects, waiting for both of them. It does not matter
    in which order they are obtained:

            yield chute.request, 'server 1', 'server 2'

    This requests and waits for 'server 1', then requests and waits for
    'server 2':

            yield chute.request, 'server 1'
            yield chute.request, 'server 2'

    Requests can also be make for one of any number of objects. For instance,
    if we had a list of ten servers and we didn't care which one we got:

            servers = ['server %d' % i for i in range(10)]
            yield chute.request, servers

    If we wanted any one of the servers and the manager:

            yield chute.request, servers, 'manager'

    Or if we wanted any two of the servers and we didn't care which, so
    long as we bothered the manager with them:

            yield chute.request, servers, servers, 'manager'
    '''
    EVENT_TYPE = 'request'

    def __init__(self, *args, **kwds):
        super(RequestEvent, self).__init__(RequestEvent.EVENT_TYPE, *args)
        self.event_args = kwds['event_args']

        # Convert each sequence of requested objects to a tuple, and
        # store it as unassigned. Once requested objects as assigned,
        # they go into the assigned set.
        self.unassigned = []
        for e in self.event_args:
            if type(e) not in (list, tuple):
                e = (e,)
            self.unassigned.append(tuple(e))

    def stop(self, simulator):
        '''Assigns any requested objects that can be to the process.'''
        if simulator.clock < self.clock:
            return False

        is_ok = True

        # Try and assign as much as possible of what is requested.
        new_unassigned = []
        for request_options in self.unassigned:
            is_assigned = False
            for option in request_options:
                # Ignore things already assigned.
                if simulator.assigned_to(self, option):
                    continue

                # Try to get this object from the simulator.
                if simulator.assign(self, option):
                    self.assigned.append(option)
                    is_assigned = True
                    break

            if not is_assigned:
                new_unassigned.append(request_options)

            # Allow is_ok to go to False, but keep trying to assing objects.
            is_ok = is_ok and is_assigned

        self.unassigned = new_unassigned
        if is_ok:
            self.stop_time = simulator.clock
        return is_ok


class HoldEvent(Event):
    '''
    Represents an event that holds assigned resources for a period of time.
    That time may be a constant:

            yield chute.hold, 42

    Or it may be a randomly generated value:

            yield chute.hold, chute.dist.exponential(0.25)

    One thing to note is that a process that is currently assigned to
    another process cannot enter a hold phase until it is released.
    '''
    EVENT_TYPE = 'hold'

    def __init__(self, *args, **kwds):
        super(HoldEvent, self).__init__(HoldEvent.EVENT_TYPE, *args)
        self.event_args = kwds['event_args']

        # Generate the time for hold.
        func = self.event_args[0]
        if callable(func):
            self.hold = func()
        else:
            self.hold = func

    def start(self, simulator):
        '''A process cannot hold if it is assigned to something else.'''
        if not simulator.clock < self.clock and simulator.hold(self):
            # This will make out next process time in the simulator be
            # the end of our hold period.
            if self.start_time is None:
                self.start_time = simulator.clock
                self.clock = self.start_time + self.hold
            return True

        return False

    def stop(self, simulator):
        '''Unhold the process if enough time has passed.'''
        if simulator.clock < self.clock:
            return False
        else:
            simulator.unhold(self)
            self.stop_time = simulator.clock
            return True


class ReleaseEvent(Event):
    '''
    Represents an event that releases assigned resources. The following
    releases everything assigned to a process:

            yield chute.release

    The following releases just one server:

            yield chute.release, 'server 1'

    And this releases two of the servers and the manager:

            yield chute.release, servers, servers, 'manager'

    A process will only release resources it is currently assigned.
    '''
    EVENT_TYPE = 'release'

    def __init__(self, *args, **kwds):
        super(ReleaseEvent, self).__init__(ReleaseEvent.EVENT_TYPE, *args)
        self.event_args = kwds['event_args']

    def _find_order(self, assigned, release_tuples, order=[]):
        '''Finds the first feasible order of resources to release.'''
        try:
            release_tup = release_tuples[0]
        except IndexError:
            return order

        # Use backtracking to build a list of items to release that
        # will satisfy all the release arguments, if such a list exists.
        for to_release in release_tup:
            if to_release in assigned:
                new_assigned = set(assigned)
                new_assigned.remove(to_release)
                new_order = self._find_order(
                    new_assigned,
                    release_tuples[1:],
                    order + [to_release]
                )

                if new_order is not False:
                    return new_order

        return False

    def stop(self, simulator):
        '''Release .'''
        if simulator.clock < self.clock:  # Sanity check.
            return False

        assigned = set(simulator.resources(self))

        if self.event_args:
            release_tuples = []
            for e in self.event_args:
                if type(e) not in (list, tuple):
                    e = assigned.intersection(set([e]))
                else:
                    e = assigned.intersection(set(e))
                release_tuples.append(e)

            # Find an order of resources to remove to satisfy release criteria.
            order = self._find_order(simulator.resources(self), release_tuples)
            if order:
                for o in order:
                    simulator.release(self, o)
                self.stop_time = simulator.clock
                return True

            return False

        else:
            # Nothing released specifically, so release everything.
            for to_release in assigned:
                simulator.release(self, to_release)
            self.stop_time = simulator.clock
            return True
