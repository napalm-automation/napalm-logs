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

    def publish(self, obj):
        pass

    def stop(self):
        pass
