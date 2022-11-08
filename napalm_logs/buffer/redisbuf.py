# -*- coding: utf-8 -*-
"""
Redis buffer interface.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

# Import pythond stdlib
import logging

try:
    import redis

    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False


log = logging.getLogger(__name__)


class RedisBuffer(object):
    """
    Memory buffer class.
    """

    def __init__(self, expire_time, **kwargs):
        self.expire_time = expire_time
        # expire_time is assumed to be in seconds
        self._key_prefix = kwargs.pop("key_prefix", "")
        self._keys_set_name = kwargs.pop("keys_set_name", "__napalm_logs_keys_set")
        self._redis = redis.StrictRedis(**kwargs)
        self._redis_pipeline = self._redis.pipeline()

    def __setitem__(self, key, val):
        key = "{prefix}{key}".format(prefix=self._key_prefix, key=key)
        self._redis_pipeline.set(key, val, ex=self.expire_time, nx=True)
        self._redis_pipeline.sadd(self._keys_set_name, key)
        self._redis_pipeline.execute()

    def __contains__(self, key):
        return True if key in self else False

    def __getitem__(self, key):
        key = "{prefix}{key}".format(prefix=self._key_prefix, key=key)
        val = self._redis.get(key)
        if val is None:
            self._redis.srem(self._keys_set_name, key)
        return val

    def items(self):
        keys = self._redis.smembers(self._keys_set_name)
        for key in keys:
            self._redis_pipeline.get(key)
        get_results = self._redis_pipeline.execute()
        key_vals = dict(zip(keys, get_results))
        for key, value in key_vals.items():
            if value:
                yield key
            else:
                self._redis_pipeline.srem(self._keys_set_name, key)
        self._redis_pipeline.execute()
