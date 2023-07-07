.. _buffer-memory:

======
Memory
======

This :ref:`buffer` interface caches the messages into memory.

.. warning::

    When running ``napalm-logs`` in environment with very hig volume of syslog
    messages, using this interface may lead to high memory consumption. To 
    control this, please check the :ref:`buffer-opts-expire-time` option to 
    fine tune this behaviour.

This interface doesn't have any specific options.
