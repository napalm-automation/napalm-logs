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
    We are unable to bind to the specified ip / port
    '''
    pass

class MissConfigurationException(NapalmLogsException):
    '''
    The configuration does not match the valid config template
    '''
    pass

class UnknownOpenConfigModel(NapalmLogsException):
    '''
    We are unable to log a model via napalm-yang
    '''
    pass

class OpenConfigPathError(NapalmLogsException):
    '''
    We are unable to set the open config path specified
    '''
    pass
