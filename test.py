#!/usr/bin/env python
# -*- coding:utf-8 -*-

# callbacks based async framework
# * non blocking sockets 2°
# * callbacks, allowing multiples operations to be waiting concurrently for i/o operations 3°
# * event loop
# * coroutines

import socket
import time

# 2° to wait for some event on a non blocking socket
# jusk ask for the default selector for your system
from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ
selector = DefaultSelector()

# client socket to retrieve something from a server
def get(path):
    s = socket.socket()
    s.setblocking(False) # socket no more blocking
    try:
        s.connect(('duckduckgo.com', 80)) # will return immediately or raise exception
    except BlockingIOError:
        pass

    request = 'GET %s HTTP/1.0\r\n\r\n' % path

    # we write a closure to pass s & request to our writable callback
    callback = lambda: writable(s, request)
    # dear selector, I'm interested in any event that may occur on this file descriptor (my socket)
    selector.register(s.fileno(), EVENT_WRITE, data=callback)


# 3° let's write a callback that will be called once the socket is writable
def writable(s, request):
    # I'm no more interested in the write event on my socket, please forget about it
    selector.unregister(s.fileno())
    # socket is writable, so we can send
    s.send(request.encode()) # un-code

    chunks = []

    # we write a closure to pass s & chunks to our callback
    callback = lambda: readable(s, chunks)
    # dear selector, I'm interested in any read event that may occur on this file descriptor
    selector.register(s.fileno(), EVENT_READ, data=callback)

def readable(s, chunks):
    # I'm no more interested in the read event on my socket, please forget about it
    selector.unregister(s.fileno())
    chunk = s.recv(1000)
    if chunk:
        chunks.append(chunk)
        # we need to ckeck if socket still readable, until the last chunk
        callback = lambda: readable(s, chunks)
        # dear selector, I'm interested in any read event that may occur on this file descriptor
        selector.register(s.fileno(), EVENT_READ, data=callback)
    else: #empty chunk, server hang up
        body = b''.join(chunks).decode() # be-code
        print(body.split('\n')[0])


start = time.time()
get('/?q=python+socket+&t=lm&ia=about')
get('/?q=golang+socket+&t=lm&ia=about')
get('/?q=rust+socket+&t=lm&ia=about')
get('/?q=erlang+socket+&t=lm&ia=about')

while True:
    # retrieve events
    events = selector.select()
    for event, mask in events:
        cb = event.data
        # whatever the event, call the callback linked to it
        cb()

# get launched serially, so final time is time for one request times number of requests
print("took %.1f sec" % (time.time() - start))
