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
        pass

    def publish(self, obj):
        pass
