chute
=====

Chute is a simple tool for running Discrete Event Simulations using Python.

Chute is under active development, but you can start using it for simulations now.

Installation
------------

Installation is pretty simple, like most other Python tools. I'm assuming UNIX here, though on other platforms the commands are similar.

```
$ easy_install chute
```

If you want to install it into your system's Python directories, run this instead.

```
$ sudo easy_install chute
```

== Writing & Running Basic Simulations ==

Simulations are intended to be as simple to create as possible. Type in the following and save it as *mm1_function.py*. This is one way an M/M/1 queue simulation might look.

```#!python
import chute

@chute.process(chute.dist.exponential(.5))
def customer():
    yield chute.request, 'server'
    yield chute.hold, chute.dist.exponential(.75)
    yield chute.release
```

Chute will create customer processes and put them into the simulation according to the interarrival distribution passed to *@chute.process* Once created, each customer requests a resource, in this case the string *'server'*. The customer is then serviced by resources it is currently holding according to some probability distribution, after which the customer releases all its resources and leaves the simulation.

Let's run this simulation. Though you can do this directly in Python, it's simpler to use the *chute* command.

```python
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

```
$ chute -n 10 -t 100 mm1_function.py | less
```

I'm piping this through *less* so it's easy to see the header. Chute runs our simulation and prints messages to standard out as events finish. This is an important design feature. Chute creates simulation output data for you, but it assumes you know how to analyze that output best yourself.

Right now you should see something like this.

```
simulation,sent time,start time,stop time,event type,process name,process instance,assigned
0,0.04649989522533239,0.04649989522533239,0.04649989522533239,create,customer,0,
0,0.04649989522533239,0.04649989522533239,0.04649989522533239,request,customer,0,server
0,1.6557438414054708,1.6557438414054708,1.6557438414054708,create,customer,1,
0,0.04649989522533239,0.04649989522533239,1.6557438414054708,hold,customer,0,server
0,1.6557438414054708,1.6557438414054708,1.6557438414054708,release,customer,0,
0,1.6557438414054708,1.6557438414054708,1.6557438414054708,request,customer,1,server
etc.
```

The default output is CSV format. The following fields are provided.

|simulation|Simulation number.|
|sent time|Time an event is sent to the simulator.|
|start time|Time an event starts processing.|
|stop time|Time that event stops processing.|
|event type|Event type (create, request, etc.).|
|process name|Process name (e.g. 'customer').|
|process instance|Process instance number (e.g. 5).|
|assigned|Resources assigned after the event is fulfilled (e.g., ['server 1', etc.]).|

If you'd prefer JSON messages, just add the *-f json* flag.

```
$ chute -f json -n 10 -t 100 mm1_function.py
```

== More Complex Simulations ==

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

== Happy Simulating ==

Thanks for looking at chute. I hope you enjoy it. It'll be changing and improving a lot, so keep checking back.

Also, the best features are user-driving. Please try writing simulations in it and make suggestions based on your experiences.
