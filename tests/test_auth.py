# -*- coding: utf-8 -*-
'''
Test the auth process.
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import pythond stdlib
import time
import logging
from multiprocessing import Process

# Import third party libs
import pytest
import nacl.utils
import nacl.secret
import nacl.signing
import nacl.encoding

# Import napalm-logs
import napalm_logs.exceptions
from napalm_logs.utils import ClientAuth
from napalm_logs.auth import NapalmLogsAuthProc

log = logging.getLogger(__name__)

AUTH_PROC = None


def _generate_test_keys():
    '''
    Generate proper PK and SGN keys.
    '''
    log.debug('Generating a testing private key')
    priv_key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    log.debug('Generating the signing key')
    signing_key = nacl.signing.SigningKey.generate()
    verify_key = signing_key.verify_key
    sgn_verify_hex = verify_key.encode(encoder=nacl.encoding.HexEncoder)
    return priv_key, sgn_verify_hex


def test_invalid_cert():
    '''
    Testing if the auth process dies when
    unable to open the SSL certificate or keyfile.
    '''
    nlap = NapalmLogsAuthProc('fake_cert', 'fake_keyfile', 'fake_pk', 'fake_hex')
    with pytest.raises(IOError):
        nlap.start()


def test_crt_missmatch():
    '''
    Forged certificate should raise napalm_logs.exceptions.SSLMismatchException.
    '''
    nlap = NapalmLogsAuthProc('tests/auth/forged.crt',
                              'tests/auth/forged.key',
                              'fake_pk',
                              'fake_hex')
    with pytest.raises(napalm_logs.exceptions.SSLMismatchException):
        nlap.start()


def test_client_auth_fail_server_down():
    '''
    Test client connect failure when server is not started yet.
    '''
    with pytest.raises(napalm_logs.exceptions.ClientConnectException):
        client = ClientAuth('tests/auth/server.crt')  # noqa


def test_successful_start():
    '''
    Test that the auth process can start properly
    when valid certificate and key are configured.
    '''
    global AUTH_PROC
    pk, sgn_key = _generate_test_keys()
    nlap = NapalmLogsAuthProc('tests/auth/server.crt',
                              'tests/auth/server.key',
                              pk,
                              sgn_key)
    AUTH_PROC = Process(target=nlap.start)
    AUTH_PROC.start()

# TODO: check why unable to stop this proc
# def test_twice_bind():
#     '''
#     Test that binding twice on the same host/port fails,
#     and raises napalm_logs.exceptions.BindException.
#     '''
#     pk, sgn_key = _generate_test_keys()
#     nlap = NapalmLogsAuthProc('tests/auth/server.crt',
#                               'tests/auth/server.key',
#                               pk,
#                               sgn_key)
#     with pytest.raises(napalm_logs.exceptions.BindException):
#         nlap.start()
#     nlap.stop()


def test_client_auth_fail_wrong_port():
    '''
    Test client connect failure on wrong server port.
    '''
    assert AUTH_PROC.is_alive()
    with pytest.raises(napalm_logs.exceptions.ClientConnectException):
        client = ClientAuth('tests/auth/server.crt',
                            port=1234)
        client.stop()


def test_client_auth():
    '''
    Test the auth process startup and a client
    that retrieves the pk and sgn key.
    '''
    assert AUTH_PROC.is_alive()
    time.sleep(.1)  # waiting for the auth socket
    client = ClientAuth('tests/auth/server.crt')
    client.stop()


def test_successful_stop():
    '''
    Test if able to stop properly the auth process.
    '''
    assert AUTH_PROC.is_alive()
    AUTH_PROC.terminate()
    AUTH_PROC.join()
