# -*- coding: utf-8 -*-
"""
ZeroMQ listener for napalm-logs.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

# Import stdlib
import time
import logging

# Import third party libs
try:
    import zmq

    HAS_ZMQ = True
except ImportError:
    HAS_ZMQ = False

# Import napalm-logs pkgs
from napalm_logs.listener.base import ListenerBase
from napalm_logs.exceptions import ListenerException

log = logging.getLogger(__name__)


class ZMQListener(ListenerBase):
    """
    ZMQ listener class.
    """

    def __init__(self, address, port, **kwargs):
        if kwargs.get("address"):
            address = kwargs["address"]
        if kwargs.get("port"):
            port = kwargs["port"]
        self.address = address
        self.port = port
        self.hwm = kwargs.get("hwm")
        self.keepalive = kwargs.get("keepalive", 1)
        self.keepalive_idle = kwargs.get("keepalive_idle", 300)
        self.keepalive_interval = kwargs.get("keepalive_interval", -1)
        self.recvtimeout = kwargs.get("timeout")
        self.protocol = kwargs.get("protocol", "tcp")
        self.type = kwargs.get("socket_type", "PULL")

    def start(self):
        """
        Startup the zmq consumer.
        """
        zmq_uri = (
            "{protocol}://{address}:{port}".format(
                protocol=self.protocol, address=self.address, port=self.port
            )
            if self.port
            else "{protocol}://{address}".format(  # noqa
                protocol=self.protocol, address=self.address
            )
        )
        log.debug("ZMQ URI: %s", zmq_uri)
        self.ctx = zmq.Context()
        if hasattr(zmq, self.type):
            skt_type = getattr(zmq, self.type)
        else:
            skt_type = zmq.PULL
        self.sub = self.ctx.socket(skt_type)
        self.sub.connect(zmq_uri)
        if self.hwm is not None:
            self.sub.setsockopt(zmq.RCVHWM, self.hwm)
        if self.recvtimeout is not None:
            log.debug("Setting RCVTIMEO to %d", self.recvtimeout)
            self.sub.setsockopt(zmq.RCVTIMEO, self.recvtimeout)
        if self.keepalive is not None:
            log.debug("Setting TCP_KEEPALIVE to %d", self.keepalive)
            self.sub.setsockopt(zmq.TCP_KEEPALIVE, self.keepalive)
        if self.keepalive_idle is not None:
            log.debug("Setting TCP_KEEPALIVE_IDLE to %d", self.keepalive_idle)
            self.sub.setsockopt(zmq.TCP_KEEPALIVE_IDLE, self.keepalive_idle)
        if self.keepalive_interval is not None:
            log.debug("Setting TCP_KEEPALIVE_INTVL to %d", self.keepalive_interval)
            self.sub.setsockopt(zmq.TCP_KEEPALIVE_INTVL, self.keepalive_interval)

    def receive(self):
        """
        Return the message received.

        ..note::
            In ZMQ we are unable to get the address where we got the message from.
        """
        try:
            msg = self.sub.recv()
        except zmq.Again as error:
            log.error("Unable to receive messages: %s", error, exc_info=True)
            raise ListenerException(error)
        log.debug("[%s] Received %s", time.time(), msg)
        return msg, ""

    def stop(self):
        """
        Shutdown zmq listener.
        """
        log.info("Stopping the zmq listener class")
        self.sub.close()
        self.ctx.term()
