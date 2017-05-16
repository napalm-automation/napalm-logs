# -*- coding: utf-8 -*-
'''
Listener worker process
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import pythond stdlib
import os
import time
import signal
import socket
import logging
import threading

# Import third party libs
import zmq
import umsgpack

# Import napalm-logs pkgs
from napalm_logs.config import LST_IPC_URL
from napalm_logs.config import BUFFER_SIZE
from napalm_logs.proc import NapalmLogsProc
# exceptions
from napalm_logs.exceptions import NapalmLogsExit

log = logging.getLogger(__name__)


class NapalmLogsListenerProc(NapalmLogsProc):
    '''
    Listener sub-process class.
    '''
    def __init__(self, socket, pipe):
        self.socket = socket
        self.pipe = pipe
        self.__up = False

    def _exit_gracefully(self, signum, _):
        log.debug('Caught signal in listener process')
        self.stop()

    def _setup_ipc(self):
        '''
        Setup the IPC publisher.
        '''
        ctx = zmq.Context()
        self.pub = ctx.socket(zmq.PUSH)
        self.pub.bind(LST_IPC_URL)

    def start(self):
        '''
        Listen to messages and queue them.
        '''
        # self._setup_ipc()
        # Start suicide polling thread
        thread = threading.Thread(target=self._suicide_when_without_parent, args=(os.getppid(),))
        thread.start()
	signal.signal(signal.SIGTERM, self._exit_gracefully)
        self.__up = True
        while self.__up:
            try:
                msg, addr = self.socket.recvfrom(BUFFER_SIZE)
            except socket.error as error:
                if self.__up is False:
                    return
                else:
                    msg = 'Received listener socket error: {}'.format(error)
                    log.error(msg, exc_info=True)
                    raise NapalmLogsExit(msg)
            # Addr contains (IP, port), we only care about the IP
            # obj = (msg, addr[0])
            # bin_obj = umsgpack.packb(obj)
            log.debug('[{2}] Received {0} from {1}. Adding in the queue'.format(msg, addr, time.time()))
            # self.pub.send(bin_obj)
            self.pipe.send((msg, addr[0]))

    def stop(self):
        log.info('Stopping listener process')
        self.__up = False
        self.socket.close()
        self.pipe.close()
