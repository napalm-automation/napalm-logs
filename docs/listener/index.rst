.. _listener:

========
Listener
========

The listener subsystem is a pluggable interface for inbound unstructured syslog
messages. The messages can be received directly from the network devices, via
UDP or TCP, or from other third parties, such as brokers, e.g. ZeroMQ, Kafka,
etc., depending on the architecture of the network. The default listener is UDP.

From the command line, the listener can be selected using the ``--listener``
option, e.g.:

.. code-block:: bash

  $ napalm-logs --listener tcp

From the configuration file, the listener can be specified using the ``listener``
option, eventually with several options. The options depend on the
nature of the listener.

Example: listener configuration using the default configuration

.. code-block:: yaml

  listener: tcp

Example: listener configuration using custom options

.. code-block:: yaml

  listener:
    tcp:
      buffer_size: 2048
      max_clients: 100

.. note::

  The IP Address / port for the listener be specified using the
  :ref:`configuration-options-address` and :ref:`configuration-options-port`
  configuration options.

Available listeners and their options
-------------------------------------

.. toctree::
   :maxdepth: 1

   udp
   tcp
   kafka
   zmq
