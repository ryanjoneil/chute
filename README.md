chute
=====

Chute is a simple tool for running Discrete Event Simulations using Python.

Chute is under active development, but you can start using it for simulations now.

Installation
------------

Installation is pretty simple, like most other Python tools. 

```bash
$ pip install chute
```

Chute supports Pythons 2 & 3, so you can also use `pip3`.

```bash
$ pip3 install chute
```

Writing & Running Basic Simulations
-----------------------------------

Simulations are intended to be as simple to create as possible. Type in the following and save it as *mm1_function.py*. This is one way an M/M/1 queue simulation might look.

```python
import chute

@chute.process(chute.dist.exponential(.5))
def customer():
    yield chute.request, 'server'
    yield chute.hold, chute.dist.exponential(.75)
    yield chute.release
```

Chute will create customer processes and put them into the simulation according to the interarrival distribution passed to *@chute.process* Once created, each customer requests a resource, in this case the string *'server'*. The customer is then serviced by resources it is currently holding according to some probability distribution, after which the customer releases all its resources and leaves the simulation.

Let's run this simulation. Though you can do this directly in Python, it's simpler to use the *chute* command.

```bash
$ chute -h
usage: chute [-h] -n NUM -t TIME [-f FMT] MODEL [MODEL ...]

Run the chute simulator.

positional arguments:
  MODEL                 model file to incorporate in the simulation

optional arguments:
  -h, --help            show this help message and exit
  -n NUM, --num NUM     number of simulations to run
  -t TIME, --time TIME  clock time to run simulation for
  -f FMT, --format FMT  csv (default) or json
```

You can see here that chute requires a number of times to run the simulation, a stop time for each run, and at least one model file. Model files are just Python files like the one we created above. You an split your processes across as many files as you like. We'll run 10 iterations of our simulation, each for a time of 100.

```bash
$ chute -n 10 -t 100 mm1_function.py | csvlook
```

I'm piping this through `csvlook` so it's easy to see the header. `csvlook` is provided by the [CSVkit](https://csvkit.readthedocs.org/) package, which you'll want to install if you don't have it. Chute runs our simulation and prints messages to standard out as events finish. This is an important design feature. Chute creates simulation output data for you, but it assumes you know how to analyze that output best yourself.

Right now you should see something like this.

```bash
$ chute examples/mmk.py -n 2 -t 10 | csvlook
```

|-------------+--------------------+--------------------+--------------------+------------+--------------+------------------+-----------|
|  simulation | sent_time          | start_time         | stop_time          | event_type | process_name | process_instance | assigned  |
|-------------+--------------------+--------------------+--------------------+------------+--------------+------------------+-----------|
|  0          | 3.1830629013237646 | 3.1830629013237646 | 3.1830629013237646 | create     | customer     | 0                |           |
|  0          | 3.1830629013237646 | 3.1830629013237646 | 3.1830629013237646 | request    | customer     | 0                | server 0  |
|  0          | 7.331792379273866  | 7.331792379273866  | 7.331792379273866  | create     | customer     | 1                |           |
|  0          | 3.1830629013237646 | 3.1830629013237646 | 7.331792379273866  | hold       | customer     | 0                | server 0  |
|  0          | 7.331792379273866  | 7.331792379273866  | 7.331792379273866  | request    | customer     | 1                | server 1  |
|  0          | 7.331792379273866  | 7.331792379273866  | 7.331792379273866  | release    | customer     | 0                |           |
|  0          | 7.331792379273866  | 7.331792379273866  | 7.396034056940286  | hold       | customer     | 1                | server 1  |
|  0          | 7.396034056940286  | 7.396034056940286  | 7.396034056940286  | release    | customer     | 1                |           |
|  0          | 7.517263740435106  | 7.517263740435106  | 7.517263740435106  | create     | customer     | 2                |           |
|  0          | 7.517263740435106  | 7.517263740435106  | 7.517263740435106  | request    | customer     | 2                | server 0  |
|  1          | 1.8732675310770137 | 1.8732675310770137 | 1.8732675310770137 | create     | customer     | 0                |           |
|  1          | 1.8732675310770137 | 1.8732675310770137 | 1.8732675310770137 | request    | customer     | 0                | server 0  |
|  1          | 4.840999697676644  | 4.840999697676644  | 4.840999697676644  | create     | customer     | 0                |           |
|  1          | 1.8732675310770137 | 1.8732675310770137 | 4.840999697676644  | hold       | customer     | 0                | server 0  |
|  1          | 4.840999697676644  | 4.840999697676644  | 4.840999697676644  | request    | customer     | 0                | server 1  |
|  1          | 4.840999697676644  | 4.840999697676644  | 4.840999697676644  | release    | customer     | 0                |           |
|  1          | 6.333409874081108  | 6.333409874081108  | 6.333409874081108  | create     | customer     | 1                |           |
|  1          | 6.333409874081108  | 6.333409874081108  | 6.333409874081108  | request    | customer     | 1                | server 0  |
|  1          | 4.840999697676644  | 4.840999697676644  | 6.440814672845858  | hold       | customer     | 0                | server 1  |
|  1          | 6.440814672845858  | 6.440814672845858  | 6.440814672845858  | release    | customer     | 0                |           |
|  1          | 6.630616227208659  | 6.630616227208659  | 6.630616227208659  | create     | customer     | 1                |           |
|  1          | 6.630616227208659  | 6.630616227208659  | 6.630616227208659  | request    | customer     | 1                | server 1  |
|  1          | 7.316337386468145  | 7.316337386468145  | 7.316337386468145  | create     | customer     | 2                |           |
|  1          | 6.630616227208659  | 6.630616227208659  | 7.316337386468145  | hold       | customer     | 1                | server 1  |
|  1          | 7.316337386468145  | 7.316337386468145  | 7.316337386468145  | release    | customer     | 1                |           |
|  1          | 7.316337386468145  | 7.316337386468145  | 7.316337386468145  | request    | customer     | 2                | server 1  |
|  1          | 6.333409874081108  | 6.333409874081108  | 7.418231003357046  | hold       | customer     | 1                | server 0  |
|  1          | 7.418231003357046  | 7.418231003357046  | 7.418231003357046  | release    | customer     | 1                |           |
|  1          | 7.316337386468145  | 7.316337386468145  | 8.688810604268717  | hold       | customer     | 2                | server 1  |
|  1          | 8.688810604268717  | 8.688810604268717  | 8.688810604268717  | release    | customer     | 2                |           |
|  1          | 9.697835520916259  | 9.697835520916259  | 9.697835520916259  | create     | customer     | 2                |           |
|  1          | 9.697835520916259  | 9.697835520916259  | 9.697835520916259  | request    | customer     | 2                | server 0  |
|-------------+--------------------+--------------------+--------------------+------------+--------------+------------------+-----------|


The default output is CSV format. The following fields are provided.

* simulation: Simulation number.
* sent_time: Time an event is sent to the simulator.
* start_time: Time an event starts processing.
* stop_time: Time that event stops processing.
* event_type: Event type (create, request, etc.).
* process_name: Process name (e.g. 'customer').
* process_instance: Process instance number (e.g. 5).
* assigned: Resources assigned after the event is fulfilled (e.g., ['server 1', etc.]).

If you'd prefer JSON messages, just add the *-f json* flag. The messages will come out as one JSON dictionary per line.

```
$ chute -f json -n 10 -t 100 mm1_function.py
```

More Complex Simulations
------------------------

A process is anything that is callable in Python. If we'd rather, we could use a Customer class instead of a function for our M/M/1 queue simulation. This would allow us to keep state and other information on our Customer instances.

```python
import chute

@chute.process(chute.dist.exponential(.5))
class Customer(object):
    def __call__(self):
        yield chute.request, 'server'
        yield chute.hold, chute.dist.exponential(.75)
        yield chute.release
```

In chute, a resource can be anything in Python. Here we're using strings because they are convenient. We could also use numbers or instances of classes. //Caveat: We're still working on getting the logic right for processes requesting other processes. For that, check back when chute 0.2 is released.//

A resource can only be held by one process at a time. If I need my process to request multiple resources, I just add them to the *chute.request* line.

```python
        yield chute.request, 'server 1', 'server 2'
```

Say I need two servers from a list of servers, but I don't care which ones I get. This will make sure that I get two and that they are not the same server. Whenever I request a list, chute will assign my process any one of the items in that list.

```python
        yield chute.request, ['server 1', 'server 2', 'server 3'], ['server 1', 'server 2', 'server 3']
```

Once every request I've made is fulfilled, my process can move on to the next line. *chute.hold* holds onto whatever resources are assigned to me. This is equivalent to being serviced by those resources.

Finally, the resources are released. Yielding *chute.release* without any arguments releases everything assigned to a process.

```python
        yield chute.release
```

Let's say I want two servers like above, then I want to release one of them and get the manager. I could do this too. Note that in the second case I'm just passing a constant amount of time to hold.

```python
        servers = ['server 1', 'server 2', 'server 3']
        yield chute.request, servers, servers
        yield chute.hold, chute.dist.exponential(.75)
        yield chute.release, servers

        yield chute.request, 'manager'
        yield chute.hold, 4
        yield chute.release
```

Happy Simulating
----------------

Thanks for looking at chute. I hope you enjoy it. It'll be changing and improving a lot, so keep checking back.

Also, the best features are user-driving. Please try writing simulations in it and make suggestions based on your experiences.
