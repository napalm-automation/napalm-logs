# -*- coding: utf-8 -*-
'''
napalm-logs server worker process
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


class NapalmLogsServerProc(NapalmLogsProc):
    def __init__(self,
                 pipe,
                 os_pipe_map,
                 config):
        self.config = config
        self.__pipe = pipe
        self.__os_pipe_map = os_pipe_map
        self.__up = False

    def _identify_os(self, msg):
        '''
        Using the prefix of the syslog message,
        we are able to identify the operating system and then continue parsing.
        '''
        return ('junos', 'crap')

    def start(self):
        '''
        Take the messages from the queue,
        inspect and identify the operating system,
        then queue the message correspondingly.
        '''
        # Start suicide polling thread
        thread = threading.Thread(target=self._suicide_when_without_parent, args=(os.getppid(),))
        thread.start()
        self.__up = True
        while self.__up:
            # Take messages from the main queue
            msg = self.__pipe.recv()
            id_os = self._identify_os(msg)
            if not id_os or not isinstance(id_os, tuple):
                # _identify_os shoudl return a non-empty tuple
                # providing the info for the device OS
                # and the core message
                continue
            dev_os, core_msg = id_os
            # Then send the message in the right queue
            self.__os_pipe_map[dev_os].send(core_msg)
