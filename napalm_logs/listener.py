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
from napalm_logs.config import TIMEOUT
from napalm_logs.config import LST_IPC_URL
from napalm_logs.config import BUFFER_SIZE
from napalm_logs.proc import NapalmLogsProc
# exceptions
from napalm_logs.exceptions import BindException
from napalm_logs.exceptions import NapalmLogsExit

log = logging.getLogger(__name__)


class NapalmLogsListenerProc(NapalmLogsProc):
    '''
    Listener sub-process class.
    '''
    def __init__(self, address, port, protocol, pipe):
        self.address = address
        self.port = port
        self.protocol = protocol
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

    def _open_socket(self, socket_type):
        '''
        Open the socket to listen for messages on
        '''
        if ':' in self.address:
            skt = socket.socket(socket.AF_INET6, socket_type)
        else:
            skt = socket.socket(socket.AF_INET, socket_type)
        return skt

    def _tcp_connection(self, conn, addr):
        log.debug('Established connection with {}'.format(addr))
        conn.settimeout(TIMEOUT)
        while True:
            try:
                msg = conn.recv(BUFFER_SIZE)
            except socket.timeout:
                log.debug('Connection {} timed out'.format(addr))
                return
            if not msg:
                log.info('Received empty message from {}'.format(addr))
                return
            log.debug('[{2}] Received {0} from {1}. Adding in the queue'.format(msg, addr, time.time()))
            self.pipe.send((msg, addr))
        log.debug('Closing connection with {}'.format(addr))
        conn.close()

    def start_tcp(self):
        '''
        Start listening for messages on TCP and queue them
        '''
        self.skt = self._open_socket(socket.SOCK_STREAM)
        try:
            self.skt.bind((self.address, self.port))
        except socket.error as msg:
            error_string = 'Unable to bind to port {} on {}: {}'.format(self.port, self.address, msg)
            log.error(error_string, exc_info=True)
            raise BindException(error_string)

        while self.__up:
            self.skt.listen(1)
            try:
                conn, addr = self.skt.accept()
            except socket.error as error:
                if self.__up is False:
                    return
                else:
                     msg = 'Received listener socket error: {}'.format(error)
                     log.error(msg, exc_info=True)
                     raise NapalmLogsExit(msg)
            thread = threading.Thread(target=self._tcp_connection, args=(conn, addr,))
            thread.start()

    def start_udp(self):
        '''
        Start listening for messages on UDP and queue them
        '''
        self.skt = self._open_socket(socket.SOCK_DGRAM)
        try:
            self.skt.bind((self.address, self.port))
        except socket.error as msg:
            error_string = 'Unable to bind to port {} on {}: {}'.format(self.port, self.address, msg)
            log.error(error_string, exc_info=True)
            raise BindException(error_string)

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

    def start(self):
        '''
        Start listening for messages on the appropriate protocol
        '''
        # self._setup_ipc()
        # Start suicide polling thread
        thread = threading.Thread(target=self._suicide_when_without_parent, args=(os.getppid(),))
        thread.start()
	signal.signal(signal.SIGTERM, self._exit_gracefully)
        self.__up = True
        if self.protocol == 'tcp':
             self.start_tcp()
        else:
            self.start_udp()

    def stop(self):
        log.info('Stopping listener process')
        self.__up = False
        self.skt.close()
        self.pipe.close()
