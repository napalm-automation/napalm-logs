# -*- coding: utf-8 -*-
'''
Syslog UDP listener for napalm-logs.
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import pythond stdlib
import time
import signal
import socket
import logging

# Import third party libs

# Import napalm-logs pkgs
from napalm_logs.config import BUFFER_SIZE
from napalm_logs.listener.base import ListenerBase
# exceptions
from napalm_logs.exceptions import ListenerException
from napalm_logs.exceptions import NapalmLogsExit

log = logging.getLogger(__name__)


class UDPListener(ListenerBase):
    '''
    UDP syslog listener class
    '''
    def __init__(self, address, port, pipe):
        self.address = address
        self.port = port
        self.pipe = pipe
        self.__up = False

    def _exit_gracefully(self, signum, _):
        log.debug('Caught signal in listener process')
        self.stop()

    def _open_socket(self, socket_type):
        '''
        Open the socket to listen for messages on
        '''
        if ':' in self.address:
            skt = socket.socket(socket.AF_INET6, socket_type)
        else:
            skt = socket.socket(socket.AF_INET, socket_type)
        return skt

    def start(self):
        '''
        Start listening for messages
        '''
        signal.signal(signal.SIGTERM, self._exit_gracefully)
        self.__up = True
        self.skt = self._open_socket(socket.SOCK_DGRAM)
        try:
            self.skt.bind((self.address, self.port))
        except socket.error as msg:
            error_string = 'Unable to bind to port {} on {}: {}'.format(self.port, self.address, msg)
            log.error(error_string, exc_info=True)
            raise ListenerException(error_string)

        while self.__up:
            try:
                msg, addr = self.skt.recvfrom(BUFFER_SIZE)
            except socket.error as error:
                if self.__up is False:
                    return
                else:
                    msg = 'Received listener socket error: {}'.format(error)
                    log.error(msg, exc_info=True)
                    raise NapalmLogsExit(msg)
            log.debug('[{2}] Received {0} from {1}. Adding in the queue'.format(msg, addr, time.time()))
            self.pipe.send((msg, addr[0]))

    def stop(self):
        log.info('Stopping listener process')
        self.__up = False
        self.skt.close()
        self.pipe.close()
