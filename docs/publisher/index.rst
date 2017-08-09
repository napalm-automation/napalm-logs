.. _publisher

=========
Publisher
=========

The publisher subsystem is a pluggable interface for outbound messages,
structured following the OpenConfig / IETF YANG models.
The messages can be published over
From the command line, the publisher can be selected using the ``--publisher``
option, e.g.:

.. code-block:: bash

  $ napalm-logs --publisher kafka

From the configuration file, the publisher can be specified using the ``publisher``
option, eventually with several options. The options depend on the
nature of the publisher.

Example: publisher configuration using the default configuration

.. code-block:: yaml

  publisher: zmq

Example: publisher configuration using custom options

.. code-block:: yaml

  publisher:
    kafka:
      topic: napalm-logs-out

.. note::

  The IP Address / port for the publisher be specified using the
  :ref:`configuration-options-publish-address` and
  :ref:`configuration-options-publish-port`
  configuration options.

Available publishers and their options:

.. toctree::
   :maxdepth: 1

   cli
   kafka
   log
   zmq

Additionally, the user can configure the following options, available to all
publishers:

.. _publisher-opts-send-raw:

``send_raw``
------------

If this option is set, all processed syslog messages, even ones that have not
matched a configured error, will be published over the specified transport.
This can be used to forward to log server for storage.

Example:

.. code-block:: yaml

  publisher:
    zmq:
      send_raw: true

.. _publisher-opts-send-unknown:

``send_unknown``
----------------

If this option is set, all processed syslog messages, even ones that have not
matched a certain operating system, will be published over the specified
transport. This can be used to forward to log server for storage.

Example:

.. code-block:: yaml

  publisher:
    kafka:
      send_unknown: true
