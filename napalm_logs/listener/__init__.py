# -*- coding: utf-8 -*-
"""
napalm-logs pluggable listener.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

# Import python std lib
import logging

# Import napalm-logs pkgs
# Exceptions
from napalm_logs.exceptions import InvalidListenerException

# Listener classes
from napalm_logs.listener.tcp import TCPListener
from napalm_logs.listener.udp import UDPListener
from napalm_logs.listener.zeromq import HAS_ZMQ
from napalm_logs.listener.zeromq import ZMQListener
from napalm_logs.listener.kafka import HAS_KAFKA
from napalm_logs.listener.kafka import KafkaListener


log = logging.getLogger(__file__)

LISTENER_LOOKUP = {
    "tcp": TCPListener,
    "udp": UDPListener,
    "*": UDPListener,  # default listener
}

if HAS_KAFKA:
    log.info("Kafka dependency seems to be installed, making kafka listener available.")
    LISTENER_LOOKUP["kafka"] = KafkaListener

if HAS_ZMQ:
    log.info("Adding ZMQ listener")
    LISTENER_LOOKUP["zmq"] = ZMQListener
    LISTENER_LOOKUP["zeromq"] = ZMQListener


def get_listener(name):
    """
    Return the listener class.
    """
    try:
        log.debug("Using %s as listener", name)
        return LISTENER_LOOKUP[name]
    except KeyError:
        msg = "Listener {} is not available. Are the dependencies installed?".format(
            name
        )
        log.error(msg, exc_info=True)
        raise InvalidListenerException(msg)


__all__ = ("get_listener",)
