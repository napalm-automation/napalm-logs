# -*- coding: utf-8 -*-
'''
napalm-logs base worker process
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import python stdlib
from queue import Queue


class NapalmLogsProc:
    def __init__(self,
                 name,
                 config,
                 transport,
                 log=None):
        self._name = name
        self._config = config
        self._transport = transport
        self._log = log
        self.__running = False

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

    def start(self, q):
        '''
        Start the worker process.
        '''
        self._q = q
        self.__running = True
        try:
            while self.__running:
                msg = self._q.get(block=True)
                # # Will wait till a message is available
                # kwargs = self._parse(self, msg)
                # oc_obj = self._emit(self, **kwargs)
                # self._publish(oc_obj)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        '''
        Stop the worker process.
        '''
        self.__running = False
