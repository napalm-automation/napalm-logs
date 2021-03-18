#!/usr/bin/env python
'''
napalm-logs client, with authentication.

Listens to the napalm-logs server started using the following settings:

napalm-logs --publish-address 127.0.0.0.1
            --publish-port 49017
            --auth-address 127.0.0.1
            --auth-port 49018
            --certificate /var/cache/napalm-logs.crt
            --keyfile /var/cache/napalm-logs.key
            --transport zmq

This client example listens to messages published via ZeroMQ (default transport).
'''
import zmq
import napalm_logs.utils

server_address = '127.0.0.1'  # --publish-address
server_port = 49017  # --publish-port
auth_address = '127.0.0.1'  # --auth-address
auth_port = 49018  # --auth-port

certificate = '/var/cache/napalm-logs.crt'  # --certificate

# Using zmq
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect(
    'tcp://{address}:{port}'.format(address=server_address, port=server_port)
)
socket.setsockopt(zmq.SUBSCRIBE, '')

auth = napalm_logs.utils.ClientAuth(certificate, address=auth_address, port=auth_port)

while True:
    raw_object = socket.recv()
    decrypted = auth.decrypt(raw_object)
    print(decrypted)
