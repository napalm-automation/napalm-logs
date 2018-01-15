.. _publisher:

=========
Publisher
=========

The Publisher subsystem is a pluggable interface for outbound messages,
structured following the OpenConfig / IETF YANG models.
The messages can be published over a variety of services -- see
:ref:`publisher-modules`.
From the command line, the Publisher module can be selected using the
``--publisher`` option, e.g.:

.. code-block:: bash

  $ napalm-logs --publisher kafka

From the configuration file, the Publisher can be specified using the
``publisher`` option, eventually with several options. The options depend on the
nature of the Publisher.

Example: publisher configuration using the default configuration

.. code-block:: yaml

  publisher: zmq

Example: publisher configuration using custom options

.. code-block:: yaml

  publisher:
    kafka:
      topic: napalm-logs-out

.. note::

  The IP Address / port for the Publisher be specified using the
  :ref:`configuration-options-publish-address` and
  :ref:`configuration-options-publish-port`
  configuration options.

Multiple publishers
-------------------

.. versionadded:: 0.4.0

It is possible to export the structured napalm-logs structured documents into 
multiple systems, over multiple channels, each with its separate configuration 
options. This feature is available only from the configuration file, e.g.:

.. code-block:: yaml

  publisher:
    - zmq:
        address: 1.2.3.4
        port: 5678
    - kafka:
        topic: napalm-logs-out
    - http:
        address: https://example.com/webhook

.. _publisher-modules:

Available publishers and their options
---------------------------------------

.. toctree::
   :maxdepth: 1

   cli
   http
   kafka
   log
   zmq

Globally available options
--------------------------

Additionally, the user can configure the following options, available to all
publishers:

.. _publisher-opts-send-raw:

``send_raw``: ``False``
-----------------------

If this option is set, all processed syslog messages, even ones that have not
matched a configured error, will be published over the specified transport.
This can be used to forward to log server for storage.

Example:

.. code-block:: yaml

  publisher:
    zmq:
      send_raw: true

.. note::

    This option is just a shortcut to the 
    :ref:`publisher-opts-error-blacklist` configuration option introduced in 
    0.4.0 (codename Crowbar), by removing the ``RAW`` error type from the 
    blacklisted message types, i.e., 

    .. code-block:: yaml

    publisher:
      zmq:
        error_blacklist:
          - UNKNOWN

.. _publisher-opts-only-raw:

``only_raw``: ``False``
-----------------------

.. versionadded:: 0.4.0

When this option is enabled, the publisher will publish *only* the syslog 
messages that could not be parsed.

Example:

.. code-block:: yaml

  publisher:
    - zmq:
        address: 1.2.3.4
        port: 1234
    - zmq:
        address: 5.6.7.8
        port: 5678
        only_raw: true

.. note::

    This option is a shortcut to the :ref:`publisher-opts-error-whitelist` 
    configuration option introduced in 0.4.0 (codename Crowbar), by adding the
    ``RAW`` message to the whitelist message types, i.e., 

    .. code-block:: yaml

      publisher:
        - zmq:
            address: 1.2.3.4
            port: 1234
        - zmq:
            address: 5.6.7.8
            port: 5678
            error_whitelist:
              - RAW

.. _publisher-opts-send-unknown:

``send_unknown``: ``False``
---------------------------

If this option is set, all processed syslog messages, even ones that have not
matched a certain operating system, will be published over the specified
transport. This can be used to forward to log server for storage.

Example:

.. code-block:: yaml

  publisher:
    kafka:
      send_unknown: true

.. note::

    This option is just a shortcut to the 
    :ref:`publisher-opts-error-blacklist` option introduced in 0.4.0 (codename 
    Crowbar), by removing the ``UNKNOWN`` message from the blacklist, i.e.,

    .. code-block:: yaml

        publisher:
          kafka:
            error_blacklist:
              - RAW

.. _publisher-opts-only-unknown:

``only_unknown``: ``False``
---------------------------

.. versionadded:: 0.4.0

When this option is configured, napalm-logs will publish *only* the structured 
documents that are marked as ``UNKNWON`` (i.e., napalm-logs was unable to parse 
the message and determine the operating system).

Example:

.. code-block:: yaml

  publisher:
    kafka:
      only_unknown: true

.. note::

    This option is a shortcut to the :ref:`publisher-opts-error-whitelist` 
    option introduced in 0.4.0 (codename Crowbar), by adding the ``UNKNOW`` 
    message type to the whitelist, i.e.,

    .. code-block:: yaml

      publisher:
        kafka:
          error_whitelist:
            - UNKNOWN

.. _publisher-opts-error-whitelist:

``error_whitelist``: ``[]``
---------------------------

Publish only the error messages included in this list. The whitelist/blacklist
logic is  implemented in such a way that if anything is added in this list,
*only* these message types will be published and nothing else.

Default: ``None`` (empty list)

Configuration example:

.. code-block:: yaml

  publisher:
    - kafka:
        error_whitelist:
          - UNKNOWN
          - RAW
    - zmq:
        error_whitelist:
          - BGP_MD5_INCORRECT
          - BGP_NEIGHBOR_STATE_CHANGED

.. _publisher-opts-error-blacklist:

``error_blacklist``: ``['RAW', 'UNKNOWN']``
-------------------------------------------

Filter out the error types publisher. The error messages included in this list 
will not be published.

Default: ``RAW, UNKNOWN`` (both ``RAW`` and ``UNKNOWN`` message types will not 
be published by default).

Configuration example:

.. code-block:: yaml

  publisher:
    - kafka:
        error_blacklist:
          - UNKNOWN
          - RAW
          - USER_ENTER_CONFIG_MODE
    - zmq:
        error_blacklist:
          - UNKNOWN

.. _publisher-opts-serializer:

``serializer``: ``msgpack``
---------------------------

The serializer to be used when publishing the structure napalm-logs document.

Default: :ref:`serializer-msgpack`.

You can specify a separate serialize per publisher, e.g.:

.. code-block:: yaml

  publisher:
    - kafka:
        serializer: json
    - cli:
        serializer: pprint
