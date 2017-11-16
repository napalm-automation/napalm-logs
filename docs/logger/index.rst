.. _logger:

======
Logger
======

.. warning::

    The Logger interface will be deprecated beginning with release 0.4.0.

The logger subsystem uses the modules from the publisher pluggable subsystem to
send partially parsed syslog messages. The configuration options are the same
as for the publisher referenced -- see the :ref:`publisher-modules`. It can be
used together with the publisher system in such a way the publisher externalizes
the fully processed objects and the clients can subscribe and collect them,
while the logger submits the partially parsed messages. This is ideal for
logging these unprocessed messages, hence the *logger* name.

This subsystem is by default disabled and it cannot be configured from the
command line, but only from the configuration file. Besides the publisher
name to be specified, it also requires to configure at least one set one of the
options below:

.. _logger-opts-send-raw:

``send_raw``
------------

If this option is set, all processed syslog messages, even ones that have not
matched a configured error, will be output via the specified transport.
This can be used to forward to log server for storage.

Example:

.. code-block:: yaml

  logger:
    kafka:
      send_raw: true

.. _logger-opts-send-unknown:

``send_unknown``
----------------

If this option is set, all processed syslog messages, even ones that have not
matched a certain operating system, will be output via the specified transport.
This can be used to forward to log server for storage.

Example:

.. code-block:: yaml

  logger:
    zmq:
      send_unknown: true
