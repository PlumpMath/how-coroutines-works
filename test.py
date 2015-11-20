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

    # dear selector, I'm interested in any event that may occur on this file descriptor (my socket)
    selector.register(s.fileno(), EVENT_WRITE)
    # wait for what I'm intested in
    selector.select()
    # I'm no more interested in the write event on my socket, please forget about it
    selector.unregister(s.fileno())
    # socket is writable, so we can send
    s.send(request.encode()) # un-code

    chunks = []
    while True:
        # dear selector, I'm interested in any event that may occur on this file descriptor (my socket)
        selector.register(s.fileno(), EVENT_READ)
        # wait for what I'm intested in
        selector.select()
        # I'm no more interested in the read event on my socket, please forget about it
        selector.unregister(s.fileno())
        chunk = s.recv(1000)
        if chunk:
            chunks.append(chunk)

        else: #empty chunk, server hang up
            body = b''.join(chunks).decode() # be-code
            print(body.split('\n')[0])
            return

start = time.time()
get('/?q=python+socket+&t=lm&ia=about')
get('/?q=golang+socket+&t=lm&ia=about')
get('/?q=rust+socket+&t=lm&ia=about')
get('/?q=erlang+socket+&t=lm&ia=about')

# get launched serially, so final time is time for one request times number of requests
print("took %.1f sec" % (time.time() - start))
