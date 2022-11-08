# -*- coding: utf-8 -*-
"""
Syslog UDP listener for napalm-logs.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

# Import pythond stdlib
import time
import socket
import logging

# Import third party libs

# Import napalm-logs pkgs
from napalm_logs.config import BUFFER_SIZE
from napalm_logs.config import REUSE_PORT
from napalm_logs.listener.base import ListenerBase

# exceptions
from napalm_logs.exceptions import BindException
from napalm_logs.exceptions import ListenerException

log = logging.getLogger(__name__)


class UDPListener(ListenerBase):
    """
    UDP syslog listener class.
    """

    def __init__(self, address, port, **kwargs):
        if kwargs.get("address"):
            self.address = kwargs["address"]
        else:
            self.address = address
        if kwargs.get("port"):
            self.port = kwargs["port"]
        else:
            self.port = port
        self.buffer_size = kwargs.get("buffer_size", BUFFER_SIZE)
        self.reuse_port = kwargs.get("reuse_port", REUSE_PORT)
        log.debug("Buffer size: %d", self.buffer_size)

    def start(self):
        """
        Create the UDP listener socket.
        """
        if ":" in self.address:
            self.skt = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        else:
            self.skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if self.reuse_port:
            self.skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if hasattr(socket, "SO_REUSEPORT"):
                self.skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            else:
                log.error("SO_REUSEPORT not supported")
        try:
            self.skt.bind((self.address, int(self.port)))
        except socket.error as msg:
            error_string = "Unable to bind to port {} on {}: {}".format(
                self.port, self.address, msg
            )
            log.error(error_string, exc_info=True)
            raise BindException(error_string)

    def receive(self):
        """
        Return the message received and the address.
        """
        try:
            msg, addr = self.skt.recvfrom(self.buffer_size)
        except socket.error as error:
            log.error("Received listener socket error: %s", error, exc_info=True)
            raise ListenerException(error)
        log.debug("[%s] Received %s from %s", msg, addr, time.time())
        return msg, addr[0]

    def stop(self):
        """
        Shut down the UDP listener.
        """
        log.info("Stopping the UDP listener")
        self.skt.close()
