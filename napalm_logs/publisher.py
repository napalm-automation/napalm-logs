# -*- coding: utf-8 -*-
'''
Listener worker process
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import pythond stdlib
import os
import time
import logging
import threading

# Import python stdlib
import umsgpack
import nacl.utils
import nacl.secret

# Import napalm-logs pkgs
from napalm_logs.proc import NapalmLogsProc
from napalm_logs.transport import get_transport

log = logging.getLogger(__name__)


class NapalmLogsPublisherProc(NapalmLogsProc):
    '''
    publisher sub-process class.
    '''
    def __init__(self,
                 address,
                 port,
                 transport_type,
                 private_key,
                 signing_key,
                 pipe,
                 disable_security=False):
        self.__pipe = pipe
        self.__up = False
        self.address = address
        self.port = port
        self.disable_security = disable_security
        self._transport_type = transport_type
        self.__safe = nacl.secret.SecretBox(private_key)
        self.__signing_key = signing_key
        self._setup_transport()

    def _setup_transport(self):
        '''
        Setup the transport.
        '''
        transport_class = get_transport(self._transport_type)
        self.transport = transport_class(self.address,
                                        self.port)

    def _prepare(self, obj):
        '''
        Prepare the object to be sent over the untrusted channel.
        '''
        # binary serialization with MessagePack
        bin_obj = umsgpack.packb(obj)
        # generating a nonce
        nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
        # encrypting using the nonce
        encrypted = self.__safe.encrypt(bin_obj, nonce)
        # sign the message
        signed = self.__signing_key.sign(encrypted)
        return signed

    def start(self):
        '''
        Listen to messages and publish them.
        '''
        # Start suicide polling thread
        thread = threading.Thread(target=self._suicide_when_without_parent, args=(os.getppid(),))
        thread.start()
        self.transport.start()
        self.__up = True
        while self.__up:
            to_publish = self.__pipe.recv()
            log.debug('Publishing object:')
            log.debug(to_publish)
            if self.disable_security is True:
                prepared_obj = umsgpack.packb(to_publish)
            else:
                prepared_obj = self._prepare(to_publish)
            self.transport.publish(prepared_obj)

    def stop(self):
        self.__up = False
