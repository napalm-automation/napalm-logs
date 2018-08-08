.. _listener-tcp:

===
TCP
===

Receive the unstructured syslog messages over TCP.

Available options:

``buffer_size``: ``1024``
-------------------------

The socket buffer size, in bytes.

Example:

.. code-block:: yaml

  listener:
    tcp:
      buffer_size: 2048

``reuse_port``: ``false``
-------------------------

Enable or disable SO_REUSEPORT on listener's socket.

Example:

.. code-block:: yaml

  listener:
    udp:
      reuse_port: true

``socket_timeout``: ``60``
--------------------------

The socket timeout, in seconds.

Example:

.. code-block:: yaml

  listener:
    tcp:
      socket_timeout: 5

``max_clients``: ``5``
----------------------

The maximum number of parallel connections to accept.

Example:

.. code-block:: yaml

  listener:
    tcp:
      max_clients: 100
