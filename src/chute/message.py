from csv import DictWriter
import json
import sys


class MessageHandler(object):
    '''Constructs a message handler for simulation logging messages.'''
    MESSAGE_FIELDS = [
        'simulation',        # Simulation number.
        'sent_time',         # Time an event is sent to the simulator.
        'start_time',        # Time an event starts processing.
        'stop_time',         # Time that event stops processing..
        'event_type',        # Event type (create, request, etc.).
        'process_name',      # Process name (e.g. 'customer')
        'process_instance',  # Process instance number (e.g. 5)
        'assigned'           # Resources assigned after the event is fulfilled
                             # (e.g., ['server 1', etc.])
    ]

    def __init__(self, out=sys.stdout, fmt='csv', header=False):
        '''
        Instantiates a simulation message handler. Parameters:

            - out (default=sys.stdout): output file handle
            - fmt (default='csv'): 'csv' or 'json'
        '''
        self.out = out
        self.fmt = fmt

        if fmt == 'csv':
            self.writer = DictWriter(self.out, self.MESSAGE_FIELDS)
            if header:
                self.writer.writeheader()

    def log(self, message):
        # Format the assigned list for CSV. For other formats
        # just use the list of strings we have.
        message = message.copy()

        for k, v in message.items():
            if type(v) not in (list, tuple, set):
                continue
            if self.fmt == 'csv':
                message[k] = ', '.join(str(x) for x in v)
            else:
                message[k] = [str(x) for x in v]

        if self.fmt == 'csv':
            self.writer.writerow(message)
        elif self.fmt == 'json':
            self.out.write(json.dumps(message) + os.linesep)
