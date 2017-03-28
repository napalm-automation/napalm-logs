# -*- coding: utf-8 -*-
'''
napalm-logs exceptions.
'''
from __future__ import absolute_import


class NapalmLogsException(Exception):
    '''
    Base exception class; all napalm-logs exceptions should inherit this.
    '''
    def __init__(self, msg=''):
        super(NapalmLogsException, self).__init__(msg)
        self.strerror = msg

class UnableToBindException(NapalmLogsException):
    '''
    When the provided IP string is neither a valid IPv4 address or a valid IPv6 address
    '''
    pass

class MissConfigurationException(NapalmLogsException):
    '''
    When the provided IP string is neither a valid IPv4 address or a valid IPv6 address
    '''
    pass
