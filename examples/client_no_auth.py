#!/usr/bin/env python
'''
napalm-logs client, without authentication.

Listens to the napalm-logs server started using the following settings:

napalm-logs --publish-address 127.0.0.0.1
            --publish-port 49017
            --transport zmq
            --disable-security

This client example listens to messages published via ZeroMQ (default transport).
'''
import zmq
import napalm_logs.utils
import json

server_address = '127.0.0.1'  # --publish-address
server_port = 49017           # --publish-port

# Using zmq
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect('tcp://{address}:{port}'.format(address=server_address,
                                               port=server_port))
socket.setsockopt(zmq.SUBSCRIBE, b'')

while True:
    raw_object = socket.recv()
    print(json.dumps(napalm_logs.utils.unserialize(raw_object)))
