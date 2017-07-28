# -*- coding: utf-8 -*-
'''
Test the auth process.
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import pythond stdlib
# Import third party libs
import pytest

# Import napalm-logs
from napalm_logs.auth import NapalmLogsAuthProc
from napalm_logs.exceptions import SSLMismatchException


def test_invalid_cert():
    '''
    Testing if the auth process dies when
    unable to open the SSL certificate or keyfile.
    '''
    nlap = NapalmLogsAuthProc('fake_cert', 'fake_keyfile', 'fake_pk', 'fake_hex')
    with pytest.raises(IOError):
        nlap.start()


def test_forger_crt():
    '''
    '''
    nlap = NapalmLogsAuthProc('/home/mircea/napalm-logs/examples/forged.crt',
                              'fake_keyfile',
                              'fake_pk',
                              'fake_hex')
    with pytest.raises(SSLMismatchException):
        nlap.start()
