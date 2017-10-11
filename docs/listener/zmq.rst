.. _listener-zmq:

======
ZeroMQ
======

.. versionadded:: 0.3.0

Receive unstructured syslog messages via ZeroMQ.

While this listener can be used without any extensive knowledge, we recommend
reading `the ZeroMQ guide <http://zguide.zeromq.org/page:all>`_ for advanced
tunning, especially when the messages are transported over networks with
misbehaving firewalls.

Available options:

``hwm``
-------

Set the high water mark for inbound messages. This option will configure the
ZeroMQ option ``ZMQ_RCVHWM``. This option controls the message queue size.
Read `this document <http://api.zeromq.org/4-1:zmq-setsockopt>`_ for more details.

Example:

.. code-block:: yaml

  listener:
    zmq:
      hwm: 0

``keepalive``: 1
----------------

Override ``SO_KEEPALIVE`` socket option.
By default, the client will try to maintain the connection alive.

Example:

.. code-block:: yaml

  listener:
    zmq:
      keepalive: 1

``keepalive_idle``: 300
-----------------------

Override ``TCP_KEEPALIVE`` socket option (where supported by OS).
The value is specified in miliseconds.

Example:

.. code-block:: yaml

  listener:
    zmq:
      keepalive_idle: 500

``keepalive_interval``: -1
--------------------------

Override ``TCP_KEEPINTVL`` socket option(where supported by OS).
The value is specified in miliseconds.

Example:

.. code-block:: yaml

  listener:
    zmq:
      keepalive_interval: 300

``timeout``
-----------

Maximum wait time (in miliseconds) to receive a message. By default does not
time out, and the listener will block waiting for a new message to arrive.

Example:

.. code-block:: yaml

  listener:
    zmq:
      timeout: 5000

``protocol``: ``tcp``
---------------------

The protocol to be used for the ZeroMQ listener. Can choose between: ``tcp``, 
``ipc``, and ``pgm``.

Example:

.. code-block:: yaml

  listener:
    zmq:
      protocol: ipc

``socket_type``: ``PULL``
-------------------------

The nature of the socket to recevie the messages. Although the user can choose
from a variety of types, ``PULL`` and ``SUB`` fit the best into napalm-logs.

Example:

.. code-block:: yaml

  listener:
    zmq:
      socket_type: SUB
