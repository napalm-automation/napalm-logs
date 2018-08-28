.. _buffer-redis:

=====
Redis
=====

This :ref:`buffer` interface caches the messages into
`Redis <https://redis.io/>`_.

.. note::

    This driver is available only when the underlying library ``redis``, 
    available as system package, or
    `Python library <https://pypi.org/project/redis/>`_.

.. _buffer-redis-opts:

Options
-------

This interface supports all the options of the
`StrictRedis class <https://redis-py.readthedocs.io/en/latest/#redis.StrictRedis>`_

Configuration example:

.. code-block:: yaml

    buffer:
      redis:
        host: redis-srv.example.com
        port: 16379
        socket_keepalive: true

In addition to the ``StrictRedis`` specific options, this interface also allows 
to configure:

.. _buffer-redis-opts-key-prefix:

``key_prefix``
~~~~~~~~~~~~~~

The prefix to be added to the Redis keys. This option defaults to empty string 
(it doesn't add any prefix).

.. _buffer-redis-opts-keys-set-name:

``keys_set_name``: ``__napalm_logs_keys_set``
---------------------------------------------

The name of the `Redis Set <https://redis.io/commands#set>`_ having the list of 
keys managed by ``napalm-logs`` to keep the cache. This is due to the fact that
``keys *`` operation is not optimal in Redis, therefore the bank of the keys is 
saved into a Redis Set for quick lookups.
