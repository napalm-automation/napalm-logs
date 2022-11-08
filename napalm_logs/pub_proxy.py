# -*- coding: utf-8 -*-
"""
Listener worker process
"""
from __future__ import absolute_import

# Import pythond stdlib
import os
import signal
import logging
import threading

# Import third party libs
import zmq

# Import napalm-logs pkgs
from napalm_logs.config import PUB_IPC_URL
from napalm_logs.config import PUB_PX_IPC_URL
from napalm_logs.proc import NapalmLogsProc

# exceptions
from napalm_logs.exceptions import NapalmLogsExit

log = logging.getLogger(__name__)


class NapalmLogsPublisherProxy(NapalmLogsProc):
    """
    Internal IPC proxy sub-process class.
    """

    def __init__(self, hwm):
        self.hwm = hwm
        self.__up = False

    def _exit_gracefully(self, signum, _):
        log.debug("Caught signal in the internal proxy process")
        self.stop()

    def _setup_ipc(self):
        """
        Setup the IPC PUB and SUB sockets for the proxy.
        """
        log.debug("Setting up the internal IPC proxy")
        self.ctx = zmq.Context()
        # Frontend
        self.sub = self.ctx.socket(zmq.SUB)
        self.sub.bind(PUB_PX_IPC_URL)
        self.sub.setsockopt(zmq.SUBSCRIBE, b"")
        log.debug("Setting HWM for the proxy frontend: %d", self.hwm)
        self.sub.setsockopt(zmq.SNDHWM, self.hwm)
        # Backend
        self.pub = self.ctx.socket(zmq.PUB)
        self.pub.bind(PUB_IPC_URL)
        log.debug("Setting HWM for the proxy backend: %d", self.hwm)
        self.pub.setsockopt(zmq.SNDHWM, self.hwm)

    def start(self):
        """
        Listen to messages and publish them.
        """
        self._setup_ipc()
        # Start suicide polling thread
        thread = threading.Thread(
            target=self._suicide_when_without_parent, args=(os.getppid(),)
        )
        thread.start()
        signal.signal(signal.SIGTERM, self._exit_gracefully)
        try:
            zmq.proxy(self.sub, self.pub)
        except zmq.ZMQError as error:
            if self.__up is False:
                log.info("Exiting on process shutdown")
                return
            else:
                log.error(error, exc_info=True)
                raise NapalmLogsExit(error)

    def stop(self):
        log.info("Stopping the internal IPC proxy")
        self.__up = False
        self.sub.close()
        self.pub.close()
        self.ctx.term()
