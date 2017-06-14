# -*- coding: utf-8 -*-
'''
napalm-logs utilities
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import pythond stdlib
import os
import ssl
import time
import signal
import socket
import logging
import threading

# Import python stdlib
import umsgpack
import nacl.secret
import nacl.signing
import nacl.encoding
from nacl.exceptions import CryptoError
from nacl.exceptions import BadSignatureError

# Import napalm-logs pkgs
import napalm_logs.config as defaults
from napalm_logs.exceptions import CryptoException
from napalm_logs.exceptions import BadSignatureException

log = logging.getLogger(__name__)


class ClientAuth:
    '''
    Client auth class.
    '''
    def __init__(self,
                 certificate,
                 address=defaults.AUTH_ADDRESS,
                 port=defaults.AUTH_PORT):
        self.certificate = certificate
        self.address = address
        self.port = port
        self.priv_key = None
        self.verify_key = None
        self.ssl_skt = None
        self.authenticate()
        self._start_keep_alive()

    def _start_keep_alive(self):
        '''
        Start the keep alive thread as a daemon
        '''
        keep_alive_thread = threading.Thread(target=self.keep_alive)
        keep_alive_thread.daemon = True
        keep_alive_thread.start()

    def keep_alive(self):
        '''
        Send a keep alive request periodically to make sure that the server
        is still alive. If not then try to reconnect.
        '''
        while True:
            self.ssl_skt.send(defaults.AUTH_KEEP_ALIVE)
            msg = self.ssl_skt.recv(len(defaults.AUTH_KEEP_ALIVE_ACK))
            if msg != defaults.AUTH_KEEP_ALIVE_ACK:
                self.ssl_skt.close()
                self.reconnect()
            time.sleep(defaults.AUTH_KEEP_ALIVE_INTERVAL)

    def reconnect(self):
        '''
        Try to reconnect and re-authenticate with the server.
        '''
        while True:
            try:
                self.authenticate()
            except socket.error:
                time.sleep(1)
            else:
                return

    def authenticate(self):
        '''
        Authenticate the client and return the private
        and signature keys.

        Establish a connection through a secured socket,
        then do the handshake using the napalm-logs
        auth algorithm.
        '''
        if ':' in self.address:
            skt_ver = socket.AF_INET6
        else:
            skt_ver = socket.AF_INET
        skt = socket.socket(skt_ver, socket.SOCK_STREAM)
        self.ssl_skt = ssl.wrap_socket(skt,
                                  ca_certs=self.certificate,
                                  cert_reqs=ssl.CERT_REQUIRED)
        self.ssl_skt.connect((self.address, self.port))
        # Explicit INIT
        self.ssl_skt.write(defaults.MAGIC_REQ)
        # Receive the private key
        private_key = self.ssl_skt.recv(defaults.BUFFER_SIZE)
        # Send back explicit ACK
        self.ssl_skt.write(defaults.MAGIC_ACK)
        # Read the hex of the verification key
        verify_key_hex = self.ssl_skt.recv(defaults.BUFFER_SIZE)
        # Send back explicit ACK
        self.ssl_skt.write(defaults.MAGIC_ACK)
        self.priv_key = nacl.secret.SecretBox(private_key)
        self.verify_key = nacl.signing.VerifyKey(verify_key_hex, encoder=nacl.encoding.HexEncoder)

    def decrypt(self, binary):
        '''
        Decrypt and unpack the original OpenConfig object,
        serialized using MessagePack.
        Raise BadSignatureException when the signature
        was forged or corrupted.
        '''
        try:
            encrypted = self.verify_key.verify(binary)
        except BadSignatureError as bserr:
            log.error('Signature was forged or corrupt', exc_info=True)
            raise BadSignatureException('Signature was forged or corrupt')
        try:
            packed = self.priv_key.decrypt(encrypted)
        except CryptoError as cerr:
            log.error('Unable to decrypt', exc_info=True)
            raise CryptoException('Unable to decrypt')
        return umsgpack.unpackb(packed)

def unserialize(binary):
    '''
    Unpack the original OpenConfig object,
    serialized using MessagePack.
    This is to be used when disable_security is set.
    '''
    return umsgpack.unpackb(binary)
