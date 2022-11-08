# -*- coding: utf-8 -*-
"""
Log transport for napalm-logs.
Send logging events across the network.
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

# Import stdlib
import logging
import logging.handlers

# Import napalm-logs pkgs
from napalm_logs.transport.base import TransportBase


class LogTransport(TransportBase):
    """
    Log transport class.
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

    def start(self):
        self.logger = logging.getLogger("napalm-logs")
        self.logger.setLevel(logging.INFO)
        handler = logging.handlers.SocketHandler(self.address, self.port)
        formatter = logging.Formatter("%(asctime)s: %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def publish(self, obj):
        self.logger.info(obj)
