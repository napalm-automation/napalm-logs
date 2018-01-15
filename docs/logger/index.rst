.. _logger:

======
Logger
======

.. deprecated:: 0.4.0

.. warning::

    The Logger interface has been deprecated beginning with release 0.4.0.
    Please use the :ref:`publisher` interface instead, using the 
    :ref:`publisher-opts-only-raw` or :ref:`publisher-opts-send-raw` Publisher 
    configuration options. For example, if you used the following configuration 
    for the Logger:

    .. code-block:: yaml

      logger:
        kafka:
          send_raw: true

    The configuration must be updated to:

    .. code-block:

      publisher:
        - kafka:
            only_raw: true

    Using ``only_raw`` is recommended to ensure that the Publisher will be used 
    only for this exact purpose. However, the user can decide what is the most 
    suitable for their use case.

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
