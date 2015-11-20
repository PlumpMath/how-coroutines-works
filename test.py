#!/usr/bin/env python
# -*- coding:utf-8 -*-

# callbacks based async framework
# * non blocking sockets 2°
# * callbacks, allowing multiples operations to be waiting concurrently for i/o operations 3°
# * event loop
# * coroutines

import socket
import time
# client socket to retrieve something from a server
def get(path):
    s = socket.socket()
    s.connect(('duckduckgo.com', 80))
    request = 'GET %s HTTP/1.0\r\n\r\n' % path
    s.send(request.encode()) # un-code

    chunks = []
    while True:

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
