# -*- coding: utf-8 -*-
'''
Authenticator worker process
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import pythond stdlib
import os
import ssl
import signal
import socket
import logging
import threading

# Import napalm-logs pkgs
from napalm_logs.config import MAGIC_REQ
from napalm_logs.config import MAGIC_ACK
from napalm_logs.proc import NapalmLogsProc
from napalm_logs.config import AUTH_MAX_CONN
from napalm_logs.exceptions import SSLMismatchException
# exceptions
from napalm_logs.exceptions import NapalmLogsExit

log = logging.getLogger(__name__)


class NapalmLogsAuthProc(NapalmLogsProc):
    '''
    Authenticator sub-process class.
    This process waits for the clients to request
    the private and signing keys.
    The communication should be established through SSL
    sockets only, the identify being verificated
    using the TLS certificate.

    Algorithm:

    Log server                    Log consumer
    -------------------------------------------
        |                               |
        | <----------- INIT ----------- |
        |                               |
        | ------- send PRV key -------> |
        |                               |
        | <------------ ACK ----------- |
        |                               |
        | ------- send SGN HEX -------> |
        |                               |
        | <------------ ACK ----------- |
    '''
    def __init__(self,
                 certificate,
                 keyfile,
                 private_key,
                 signature_hex,
                 skt):
        self.certificate = certificate
        self.keyfile = keyfile
        self.__key = private_key
        self.__sgn = signature_hex
        self.socket = skt
        self.__up = False

    def _exit_gracefully(self, signum, _):
        self.stop()

    def _handshake(self, conn, addr):
        '''
        Ensures that the client receives the AES key.
        '''
        # waiting for the magic request message
        msg = conn.recv(len(MAGIC_REQ))
        log.debug('Received message {0} from {1}'.format(msg, addr))
        if msg != MAGIC_REQ:
            log.warning('{0} is not a valid REQ message from {1}'.format(msg, addr))
            return
        log.debug('Sending the private key')
        conn.send(self.__key)
        # wait for explicit ACK
        log.debug('Waiting for the client to confirm')
        msg = conn.recv(len(MAGIC_ACK))
        if msg != MAGIC_ACK:
            return
        log.debug('Sending the signature key')
        conn.send(self.__sgn)
        # wait for explicit ACK
        log.debug('Waiting for the client to confirm')
        msg = conn.recv(len(MAGIC_ACK))
        if msg != MAGIC_ACK:
            return
        log.info('{0} is now authenticated'.format(addr))
        log.debug('Shutting down the connection with {0}'.format(addr))
        conn.shutdown(socket.SHUT_RDWR)
        log.debug('Closing the connection with {0}'.format(addr))
        conn.close()
        # https://msdn.microsoft.com/en-us/library/ms738547(VS.85).aspx

    def verify_cert(self):
        '''
        Checks that the provided cert and key are valid and usable
        '''
        try:
            ssl.create_default_context().load_cert_chain(self.certificate, keyfile=self.keyfile)
        except ssl.SSLError:
            error_string = 'SSL certificate and key do not match'
            log.error(error_string)
            raise SSLMismatchException(error_string)
        except IOError:
            log.error('Unable to open either certificate or key file')
            raise

    def start(self):
        '''
        Listen to auth requests and send the AES key.
        Each client connection starts a new thread.
        '''
        # Start suicide polling thread
        thread = threading.Thread(target=self._suicide_when_without_parent, args=(os.getppid(),))
        thread.start()
        signal.signal(signal.SIGTERM, self._exit_gracefully)
        self.__up = True
        self.socket.listen(AUTH_MAX_CONN)
        while self.__up:
            try:
                (clientsocket, address) = self.socket.accept()
                wrapped_auth_skt = ssl.wrap_socket(clientsocket,
                                                   server_side=True,
                                                   certfile=self.certificate,
                                                   keyfile=self.keyfile)
            except ssl.SSLError:
                log.exception('SSL error', exc_info=True)
                continue
            except socket.error as error:
                if self.__up is False:
                    return
                else:
                    msg = 'Received auth socket error: {}'.format(error)
                    log.error(msg, exc_info=True)
                    raise NapalmLogsExit(msg)
            log.info('{0} connected'.format(address))
            log.debug('Starting the handshake')
            client_thread = threading.Thread(target=self._handshake,
                                             args=(wrapped_auth_skt, address))
            client_thread.start()

    def stop(self):
        log.info('Stopping auth process')
        self.__up = False
        self.socket.close()
