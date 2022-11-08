# -*- coding: utf-8 -*-
"""
napalm-logs pluggable buffer interface.
"""
from __future__ import absolute_import, unicode_literals

# Import python std lib
import logging

# Import napalm-logs pkgs
# Exceptions
from napalm_logs.exceptions import InvalidBufferException

# Import buffer classes
from napalm_logs.buffer.memory import MemoryBuffer
from napalm_logs.buffer.redisbuf import RedisBuffer

log = logging.getLogger(__file__)

BUFFER_LOOKUP = {
    "mem": MemoryBuffer,
    "memory": MemoryBuffer,
    "cache": MemoryBuffer,
    "redis": RedisBuffer,
}


def get_interface(name):
    """
    Return the serialize function.
    """
    try:
        log.debug("Using %s as buffer interface", name)
        return BUFFER_LOOKUP[name]
    except KeyError:
        msg = "Buffer interface {} is not available".format(name)
        log.error(msg, exc_info=True)
        raise InvalidBufferException(msg)


__all__ = ("get_interface",)
