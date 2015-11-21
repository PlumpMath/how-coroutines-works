#!/usr/bin/env python
# -*- coding:utf-8 -*-

# callbacks based async framework
# * non blocking sockets 2°
# * callbacks, allowing multiples operations to be waiting concurrently for i/o operations 3°
# * event loop 3°
# * coroutines 4°
# --> Future
# --> generators
# --> Task, responsible for calling next() on the generators


import socket
import time

# 2° to wait for some event on a non blocking socket
# jusk ask for the default selector for your system
from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ
selector = DefaultSelector()
n_tasks = 0


# a Future represent some pending event we're waiting for
class Future:
    def __init__(self):
        self.callbacks = [] # what to do when event occurs

    def resolve(self):
        for c in self.callbacks:
            c()

class Task:
    def __init__(self, gen):
        self.gen = gen
        self.step() # to first execute the part before the yield instruction

    def step(self):
        try:
            # generator will yield a future, let's capture that
            f = next(self.gen)
        except StopIteration:
            return

        # once the future is ready,
        # prepare another call to next(self.gen) again,
        # that will execute the part after the yield instruction
        f.callbacks.append(self.step)


# client socket to retrieve something from a server
def get(path):
    global n_tasks
    n_tasks += 1

    s = socket.socket()
    s.setblocking(False) # socket no more blocking
    try:
        s.connect(('duckduckgo.com', 80)) # will return immediately or raise exception
    except BlockingIOError:
        pass

    request = 'GET %s HTTP/1.0\r\n\r\n' % path

    f = Future()
    # dear selector, I'm interested in any event that may occur on this file descriptor (my socket)
    selector.register(s.fileno(), EVENT_WRITE, data=f)
    # how to pause until s is writable?
    yield f

    # I'm no more interested in the write event on my socket, please forget about it
    selector.unregister(s.fileno())
    # socket is writable, so we can send
    s.send(request.encode()) # un-code

    chunks = []

    while True:
        f = Future()
        # dear selector, I'm interested in any read event that may occur on this file descriptor
        selector.register(s.fileno(), EVENT_READ, data=f)
        # how to pause until s is readable
        yield f
        # I'm no more interested in the read event on my socket, please forget about it
        selector.unregister(s.fileno())

        chunk = s.recv(1000)
        if chunk:
            chunks.append(chunk)
        else: #empty chunk, server hang up
            body = b''.join(chunks).decode() # be-code
            print(body.split('\n')[0])
            n_tasks -= 1
            return

start = time.time()

# we need now to create our tasks
# a task get a generator
# then call next to execute the first part, before yied
Task(get('/?q=python+socket+&t=lm&ia=about'))
Task(get('/?q=golang+socket+&t=lm&ia=about'))
Task(get('/?q=rust+socket+&t=lm&ia=about'))
Task(get('/?q=erlang+socket+&t=lm&ia=about'))
Task(get('/?q=python+socket+&t=lm&ia=about'))
Task(get('/?q=golang+socket+&t=lm&ia=about'))
Task(get('/?q=rust+socket+&t=lm&ia=about'))
Task(get('/?q=erlang+socket+&t=lm&ia=about'))
Task(get('/?q=python+socket+&t=lm&ia=about'))
Task(get('/?q=golang+socket+&t=lm&ia=about'))
Task(get('/?q=rust+socket+&t=lm&ia=about'))
Task(get('/?q=erlang+socket+&t=lm&ia=about'))
Task(get('/?q=python+socket+&t=lm&ia=about'))
Task(get('/?q=golang+socket+&t=lm&ia=about'))
Task(get('/?q=rust+socket+&t=lm&ia=about'))
Task(get('/?q=erlang+socket+&t=lm&ia=about'))


while n_tasks:
    # retrieve events
    events = selector.select()
    for event, mask in events:
        future = event.data # retrieve the future
        # call the callbacks associated to the future
        future.resolve()

# get launched serially, so final time is time for one request times number of requests
print("took %.1f sec" % (time.time() - start))
