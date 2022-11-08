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
import umsgpack
from prometheus_client import Counter

# Import napalm-logs pkgs
from napalm_logs.config import LST_IPC_URL
from napalm_logs.proc import NapalmLogsProc
from napalm_logs.listener import get_listener
from napalm_logs.exceptions import NapalmLogsExit
from napalm_logs.exceptions import ListenerException

log = logging.getLogger(__name__)


class NapalmLogsListenerProc(NapalmLogsProc):
    """
    publisher sub-process class.
    """

    def __init__(
        self,
        opts,
        address,
        port,
        listener_type,
        # pipe,
        listener_opts=None,
    ):
        self.__up = False
        self.opts = opts
        self.address = address
        self.port = port
        # self.pipe = pipe
        self._listener_type = listener_type
        self.listener_opts = {} or listener_opts

    def _exit_gracefully(self, signum, _):
        log.debug("Caught signal in the listener process")
        self.stop()

    def _setup_listener(self):
        """
        Setup the transport.
        """
        listener_class = get_listener(self._listener_type)
        self.address = self.listener_opts.pop("address", self.address)
        self.port = self.listener_opts.pop("port", self.port)
        self.listener = listener_class(self.address, self.port, **self.listener_opts)

    def _setup_ipc(self):
        """
        Setup the listener ICP pusher.
        """
        log.debug("Setting up the listener IPC pusher")
        self.ctx = zmq.Context()
        self.pub = self.ctx.socket(zmq.PUSH)
        self.pub.connect(LST_IPC_URL)
        log.debug("Setting HWM for the listener: %d", self.opts["hwm"])
        self.pub.setsockopt(zmq.SNDHWM, self.opts["hwm"])

    def start(self):
        """
        Listen to messages and publish them.
        """
        # counter metrics for messages
        c_logs_ingested = Counter(
            "napalm_logs_listener_logs_ingested",
            "Count of ingested log messages",
            ["listener_type", "address", "port"],
        )
        c_messages_published = Counter(
            "napalm_logs_listener_messages_published",
            "Count of published messages",
            ["listener_type", "address", "port"],
        )
        self._setup_ipc()
        log.debug("Using the %s listener", self._listener_type)
        self._setup_listener()
        self.listener.start()
        # Start suicide polling thread
        thread = threading.Thread(
            target=self._suicide_when_without_parent, args=(os.getppid(),)
        )
        thread.start()
        signal.signal(signal.SIGTERM, self._exit_gracefully)
        self.__up = True
        while self.__up:
            try:
                log_message, log_source = self.listener.receive()
            except ListenerException as lerr:
                if self.__up is False:
                    log.info("Exiting on process shutdown")
                    return
                else:
                    log.error(lerr, exc_info=True)
                    raise NapalmLogsExit(lerr)
            log.debug(
                "Received %s from %s. Queueing to the server.", log_message, log_source
            )
            if not log_message:
                log.info(
                    "Empty message received from %s. Not queueing to the server.",
                    log_source,
                )
                continue
            c_logs_ingested.labels(
                listener_type=self._listener_type, address=self.address, port=self.port
            ).inc()
            self.pub.send(umsgpack.packb((log_message, log_source)))
            c_messages_published.labels(
                listener_type=self._listener_type, address=self.address, port=self.port
            ).inc()

    def stop(self):
        log.info("Stopping the listener process")
        self.__up = False
        self.pub.close()
        self.ctx.term()
        # self.pipe.close()
        self.listener.stop()
