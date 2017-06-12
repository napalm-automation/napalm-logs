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


class BindException(NapalmLogsException):
    '''
    Exception raised when unable to bind the listener to the specified IP
    address / port. Either the values are not correct, either another processs
    is already using them.
    '''
    pass


class ListenerException(NapalmLogsException):
    '''
    Exception raised when encountering an exception in a listener process
    '''
    pass


class ConfigurationException(NapalmLogsException):
    '''
    Exception thrown when the user configuration is not correct.
    '''
    pass


class UnknownOpenConfigModel(NapalmLogsException):
    '''
    Unable to log a model via napalm-yang
    '''
    pass


class OpenConfigPathException(NapalmLogsException):
    '''
    Unable to set the open config path specified.
    '''
    pass


class NapalmLogsExit(NapalmLogsException):
    '''
    Raised on unexpected exit.
    '''
    pass


class CryptoException(NapalmLogsException):
    '''
    Raised when unable to decrypt.
    '''
    pass


class BadSignatureException(NapalmLogsException):
    '''
    Raised when the signature was forged or corrupted.
    '''
    pass


class SSLMismatchException(NapalmLogsException):
    '''
    Raised when the SSL certificate and key do not match
    '''
    pass
