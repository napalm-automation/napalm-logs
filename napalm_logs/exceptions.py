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
