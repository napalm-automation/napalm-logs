# -*- coding: utf-8 -*-
'''
Authenticator worker process
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import pythond stdlib
import os
import select
import logging
import hashlib
import threading

# Import napalm-logs pkgs
from napalm_logs.config import MAGIC_REQ
from napalm_logs.config import MAGIC_ACK
from napalm_logs.proc import NapalmLogsProc

log = logging.getLogger(__name__)


class NapalmLogsAuthProc(NapalmLogsProc):
    '''
    Authenticator sub-process class.
    This process waits for the clients to request
    the private AES key. The current process (i.e. server)
    does not require authentication, as the client initiates
    the connection.
    The purpose of setting up of the authentication
    is that the clients to trust the messages arrived in,
    not the opposite.
    The communication should be established through SSL
    sockets only, ideally using certificates,
    therefore safe agains MITM etc.

    Algorithm:

    Log server                    Log consumer
    -------------------------------------------
        |                               |
        | <----------- INIT ----------- |
        |                               |
        | ------- send AES key -------> |
        |                               |
        | <------------ ACK ----------- |
        |                               |
    '''
    def __init__(self, aes, skt):
        self.__aes = aes
        self.socket = skt
        self.__up = False

    def _handshake(self, conn, addr):
        '''
        Ensures that the client receives the AES key.
        '''
        # waiting for the magic request message
        msg, addr = conn.recv(len(MAGIC_REQ))
        log.debug('Received message {0} from {1}'.format(msg, addr))
        if msg != MAGIC_REQ:
            log.warning('{0} is not a valid REQ message from {1}'.format(msg, addr))
            return
        log.debug('Sending the AES key')
        conn.send(self.__aes)
        # wait for explicit ACK
        log.debug('Waiting for the client to confirm')
        msg = conn.recv(len(MAGIC_ACK))
        if msg != MAGIC_ACK:
            return
        log.info('{1} is now authenticated'.format(addr))
        log.debug('Closing the connection with {0}'.format(addr))
        conn.close()

    def start(self):
        '''
        Listen to auth requests and send the AES key.
        Each client connection starts a new thread.
        '''
        # Start suicide polling thread
        thread = threading.Thread(target=self._suicide_when_without_parent, args=(os.getppid(),))
        thread.start()
        self.__up = True
        while self.__up:
            (clientsocket, address) = serversocket.accept()
            log.info('{0} connected'.format(address))
            log.debug('Starting the handshake')
            client_thread = threading.Thread(target=self._handshake,
                                             args=(clientsocket, address))
            client_thread.start()

    def stop(self):
        self.__up = False
