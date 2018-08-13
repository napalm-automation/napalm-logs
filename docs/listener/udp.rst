.. _listener-udp:

===
UDP
===

Receive the unstructured syslog messages over UDP.

Available options:

.. _listener-udp-buffer-size:

``buffer_size``: ``1024``
-------------------------

The socket buffer size, in bytes.

Example:

.. code-block:: yaml

  listener:
    udp:
      buffer_size: 2048


.. _listener-udp-reuse-port:

``reuse_port``: ``false``
-------------------------

.. versionadded:: 0.6.0

Enable or disable ``SO_REUSEPORT`` on listener's socket.

Example:

.. code-block:: yaml

  listener:
    udp:
      reuse_port: true
