# -*- coding: utf-8 -*-
'''
ZeroMQ transport for napalm-logs.
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import third party libs
import zmq

# Import napalm-logs pkgs
from napalm_logs.transport.base import TransportBase


class ZMQTransport(TransportBase):
    '''
    ZMQ transport class.
    '''
    def __init__(self, addr, port):
        self.context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.bind('tcp://{addr}:{port}'.format(
            addr=addr,
            port=port)
        )

    def publish(self, obj):
        self.socket.send(obj)
