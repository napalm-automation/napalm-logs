# -*- coding: utf-8 -*-
'''
napalm-logs listener worker process
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import pythond stdlib
import os
import threading
import logging

# Import napalm-logs pkgs
from napalm_logs.proc import NapalmLogsProc

log = logging.getLogger(__name__)


class NapalmLogsListenerProc(NapalmLogsProc):
    def __init__(self,
                 hostname,
                 port,
                 pipe):
        self.hostname = hostname
        self.port = port
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
            # TODO listen to messages on the syslog socket
            msg = 'crap'
            self.__pipe.send(msg)
            # TODO only take the message and queue it directly
