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
import napalm_logs.config as defaults
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


def _get_proc_class(port):
    '''
    Return the testing napalm-logs authenticator class.
    '''
    pk, sgn_key = _generate_test_keys()
    nlap = NapalmLogsAuthProc('tests/auth/server.crt',
                              'tests/auth/server.key',
                              pk,
                              sgn_key,
                              auth_port=port)
    return nlap


def _start_proc(port=49018):
    '''
    Helper to start a process where we run the napalm-logs authenticator.
    '''
    nlap = _get_proc_class(port)
    proc = Process(target=nlap.start)
    proc.start()
    return proc


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
        client = ClientAuth('tests/auth/server.crt',  # noqa
                            max_try=1,
                            timeout=.1)


def test_successful_start():
    '''
    Test that the auth process can start properly
    when valid certificate and key are configured.
    '''
    proc = _start_proc(port=17171)
    proc.terminate()


def test_client_auth_fail_wrong_port():
    '''
    Test client connect failure on wrong server port.
    '''
    proc = _start_proc(port=17173)
    time.sleep(.1)
    with pytest.raises(napalm_logs.exceptions.ClientConnectException):
        client = ClientAuth('tests/auth/server.crt',
                            port=1234,
                            max_try=1,
                            timeout=.1)
        client.stop()
    proc.terminate()


def test_client_auth():
    '''
    Test the auth process startup and a client
    that retrieves the pk and sgn key.
    '''
    proc = _start_proc(port=17174)
    time.sleep(.1)  # waiting for the auth socket
    client = ClientAuth('tests/auth/server.crt', port=17174)
    client.stop()
    proc.terminate()


def test_client_keep_alive():
    '''
    Test that the client receives keepalives from
    the auth process.
    '''
    proc = _start_proc(port=17175)
    time.sleep(.1)
    client = ClientAuth('tests/auth/server.crt',
                        max_try=1,
                        timeout=.1,
                        port=17175)
    time.sleep(.1)  # wait for the client socket
    client.ssl_skt.close()  # force client socket close
    # wait for another keepalive exchange
    time.sleep(defaults.AUTH_KEEP_ALIVE_INTERVAL)
    client.stop()
    # client.stop() tries to close the auth SSL socket
    # if not alive anymore, this will raise an exception
    # therefore the test will fail
    proc.terminate()
