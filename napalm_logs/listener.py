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
from napalm_logs.config import BUFFER_SIZE
from napalm_logs.proc import NapalmLogsProc

log = logging.getLogger(__name__)


class NapalmLogsListenerProc(NapalmLogsProc):
    '''
    Listener sub-process class.
    '''
    def __init__(self,
                 socket,
                 pipe):
        self.socket = socket
        self.__pipe = pipe
        self.__up = False

    def start(self):
        '''
        Listen to messages and queue them.
        '''
        # Start suicide polling thread
        thread = threading.Thread(target=self._suicide_when_without_parent, args=(os.getppid(),))
        thread.start()
        self.__up = True
        while self.__up:
            msg, addr = self.socket.recvfrom(BUFFER_SIZE)
            # Addr contains (IP, port), we only care about the IP
            self.__pipe.send((msg, addr[0]))

    def stop(self):
        self.__up = False
