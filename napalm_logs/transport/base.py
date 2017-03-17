# -*- coding: utf-8 -*-
'''
napalm-logs transport base.
'''


class TransportBase:
    '''
    The base class for the transport.
    '''
    def __init__(self, addr, port):
        pass

    def start(self):
        pass

    def serialise(self, obj):
        pass

    def publish(self, obj):
        pass

    def tear_down(self):
        pass
