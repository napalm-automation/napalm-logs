# -*- coding: utf-8 -*-
'''
Device worker process
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import python stdlib
import os
import logging
import threading

# Import napalm-logs pkgs
from napalm_logs.proc import NapalmLogsProc

log = logging.getLogger(__name__)


class NapalmLogsDeviceProc(NapalmLogsProc):
    '''
    Device sub-process class.
    '''
    def __init__(self,
                 name,
                 config,
                 transport,
                 pipe):
        self._name = name
        self._config = config
        self._transport = transport
        self._pipe = pipe
        self.__up = False

    def __del__(self):
        self.stop()
        # Make sure to close the pipe
        self._pipe.close()
        delattr(self, '_pipe')

    def _parse(self, msg):
        '''
        Parse a syslog message and check what OpenConfig object should
        be generated.
        '''
        pass

    def _emit(self, **kwargs):
        '''
        Emit an OpenConfig object given a certain combination of
        fields mappeed in the config to the corresponding hierarchy.
        '''
        pass

    def _publish(self, obj):
        '''
        Publish the OC object.
        '''
        self._transport.publish(obj)

    def start(self):
        '''
        Start the worker process.
        '''
        # Start suicide polling thread
        thread = threading.Thread(target=self._suicide_when_without_parent, args=(os.getppid(),))
        thread.start()
        self.__up = True
        while self.__up:
            msg = self._pipe.recv()
            # # Will wait till a message is available
            # kwargs = self._parse(self, msg)
            # oc_obj = self._emit(self, **kwargs)
            # self._publish(oc_obj)

    def stop(self):
        '''
        Stop the worker process.
        '''
        self.__up = False
