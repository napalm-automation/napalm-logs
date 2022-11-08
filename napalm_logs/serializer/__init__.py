# -*- coding: utf-8 -*-
"""
napalm-logs pluggable serializer.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

# Import python std lib
import json
import yaml
import pprint
import logging

# Import third party libs
import umsgpack

# Import napalm-logs pkgs
# Exceptions
from napalm_logs.exceptions import InvalidSerializerException


log = logging.getLogger(__file__)

SERIALIZER_LOOKUP = {
    "msgpack": umsgpack.packb,
    "json": json.dumps,
    "str": str,
    "yaml": yaml.safe_dump,
    "pprint": pprint.pformat,
    "*": umsgpack.packb,  # default serializer
}


def get_serializer(name):
    """
    Return the serialize function.
    """
    try:
        log.debug("Using %s as serializer", name)
        return SERIALIZER_LOOKUP[name]
    except KeyError:
        msg = "Serializer {} is not available".format(name)
        log.error(msg, exc_info=True)
        raise InvalidSerializerException(msg)


__all__ = ("get_listener",)
