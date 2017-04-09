# -*- coding: utf-8 -*-
'''
Authenticator worker process
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import pythond stdlib
import os
import logging
import hashlib
import threading

# Import third party libs
import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random

# Import napalm-logs pkgs
from napalm_logs.config import MAGIC_OK
from napalm_logs.config import MAGIC_REQ
from napalm_logs.config import MAGIC_ACK
from napalm_logs.config import RSA_LENGTH
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
    '''
    def __init__(self,
                 aes,
                 socket):
        self.__aes = aes
        self.__socket = socket
        self.__up = False

    def _generate_rsa(self):
        '''
        Generate the RSA key.
        '''
        pass

    def start(self):
        '''
        Listen to auth requests and send the AES key encrypted
        in the RSA key.
        '''
        # Start suicide polling thread
        thread = threading.Thread(target=self._suicide_when_without_parent, args=(os.getppid(),))
        thread.start()
        self.__up = True
        while self.__up:
            # waiting for the magic request message
            msg, addr = self.__socket.recv(len(MAGIC_REQ))
            log.debug('Received message {0} from {1}'.format(msg, addr))
            if msg != MAGIC_REQ:
                log.warning('{0} is not a valid REQ message from {1}'.format(msg, addr))
                continue
            pubkey = self._generate_rsa()
            # TODO: hash and sign
            # then send
            log.debug('Sending the new generate RSA public key')
            self.__socket.send(pubkey)
            # waiting for explicit acknowledge
            log.debug('Waiting for the client to confirm the receival')
            msg = self.__socket.recv(len(MAGIC_ACK))
            if msg != MAGIC_ACK:
                continue
            # TODO: encrypt the AES with the RSA
            log.debug('Sending the AES key encrypted')
            self.__socket.send(encrypted)
            # wait for explicit OK
            log.debug('Waiting for the client to confirm')
            msg = self.__socket.recv(len(MAGIC_OK))
            if msg != MAGIC_OK:
                continue
            log.info('{1} is now authenticated'.format(addr))

    def stop(self):
        self.__up = False
