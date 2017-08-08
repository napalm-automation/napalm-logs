# -*- coding: utf-8 -*-
'''
napalm-logs listener base.
'''
from napalm_logs.proc import NapalmLogsProc


class ListenerBase(NapalmLogsProc):
    '''
    The base class for the listener.
    '''
    def __init__(self, address, port, **kwargs):
        pass

    def start(self):
        pass

    def publish(self, obj):
        pass

    def stop(self):
        pass
