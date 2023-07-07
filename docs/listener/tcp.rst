.. _listener-tcp:

===
TCP
===

Receive the unstructured syslog messages over TCP.

Available options:

.. _listener-tcp-buffer-size:

``buffer_size``: ``1024``
-------------------------

The socket buffer size, in bytes.

Example:

.. code-block:: yaml

  listener:
    tcp:
      buffer_size: 2048


.. _listener-tcp-reuse-port:

``reuse_port``: ``false``
-------------------------

.. versionadded:: 0.6.0

Enable or disable ``SO_REUSEPORT`` on listener's socket.

Example:

.. code-block:: yaml

  listener:
    tcp:
      reuse_port: true


.. _listener-tcp-socket-timeout:

``socket_timeout``: ``60``
--------------------------

The socket timeout, in seconds.

Example:

.. code-block:: yaml

  listener:
    tcp:
      socket_timeout: 5


.. _listener-tcp-max-clients:

``max_clients``: ``5``
----------------------

The maximum number of parallel connections to accept.

Example:

.. code-block:: yaml

  listener:
    tcp:
      max_clients: 100
