# -*- coding: utf-8 -*-
'''
ZeroMQ transport for napalm-logs.
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import stdlib
import json

# Import third party libs
import zmq

# Import napalm-logs pkgs
from napalm_logs.transport.base import TransportBase


class ZMQTransport(TransportBase):
    '''
    ZMQ transport class.
    '''
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port

    def start(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind('tcp://{addr}:{port}'.format(
            addr=self.addr,
            port=self.port)
        )

    def serialise(self, obj):
        return json.dumps(obj)

    def publish(self, obj):
        self.socket.send(
            self.serialise(obj)
        )

    def tear_down(self):
        if hasattr(self, 'socket'):
            self.socket.close()
        if hasattr(self, 'context'):
            self.context.term()
