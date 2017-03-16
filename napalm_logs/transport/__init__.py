# -*- coding: utf-8 -*-
'''
napalm-logs pluggable publisher.
'''
from __future__ import absolute_import
from __future__ import unicode_literals


class TransportBase:
    '''
    The base class for the transport.
    '''
    def __init__(self, addr, port):
        pass

    def publish(self, obj):
        pass
