.. _listener-udp:

===
UDP
===

Receive the unstructured syslog messages over UDP.

Available options:

``buffer_size``: ``1024``
-------------------------

The socket buffer size, in bytes.

Example:

.. code-block:: yaml

  listener:
    udp:
      buffer_size: 2048
