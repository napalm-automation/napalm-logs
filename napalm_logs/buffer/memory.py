# -*- coding: utf-8 -*-
"""
In-memory buffer interface.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

# Import pythond stdlib
import logging
import datetime

log = logging.getLogger(__name__)


class MemoryBuffer(object):
    """
    Memory buffer class.
    """

    def __init__(self, expire_time, **kwargs):
        self.expire_time = expire_time
        self.expire_time_delta = datetime.timedelta(0, expire_time, 0)
        # expire_time is assumed to be in seconds
        self._cache = {}

    def __setitem__(self, key, val):
        self._cache[key] = {"data": val, "timestamp": datetime.datetime.utcnow()}

    def __contains__(self, key):
        return True if key in self._cache else False

    def __getitem__(self, key):
        try:
            item = self._cache[key]
        except KeyError:
            return None
        if datetime.datetime.utcnow() - item["timestamp"] < self.expire_time_delta:
            return item["data"]
        else:
            del self._cache[key]
            return None

    def items(self):
        keys = list(self._cache)
        for key in keys:
            val = self[key]
            if val:
                yield key
