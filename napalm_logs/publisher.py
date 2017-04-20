# -*- coding: utf-8 -*-
'''
Listener worker process
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import pythond stdlib
import os
import logging
import threading

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
                 pipe):
        self.__pipe = pipe
        self.__up = False
        self.address = address
        self.port = port
        self._transport_type = transport_type
        self._setup_transport()

    def _setup_transport(self):
        '''
        Setup the transport.
        '''
        transport_class = get_transport(self._transport_type)
        self.transport = transport_class(self.address,
                                        self.port)

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
	    self.transport.publish(to_publish)

    def stop(self):
        self.__up = False
