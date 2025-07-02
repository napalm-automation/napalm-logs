.. _configuration-options:

=====================
Configuration Options
=====================

Here we will list all options and what they do.

Command Line
++++++++++++

All of the command line arguments can also be added to a config file.

.. _configuration-options-address:

``address``
-----------

The IP address to use to listen for all incoming syslog messages. When using
multiple listeners, it is recommended to specify this option for each listener.

Default: ``0.0.0.0``.

CLI usage example:

.. code-block:: bash

  $ napalm-logs -a 172.17.17.1
  $ napalm-logs --address 172.17.17.1

Configuration file example:

.. code-block:: yaml

  address: 172.17.17.1

.. _configuration-options-auth-address:

``auth-address``
----------------

The IP address to listen on for incoming authorisation requests.

Default: ``0.0.0.0``.

CLI usage example:

.. code-block:: bash

  $ napalm-logs --auth-address 172.17.17.2

Configuration file example:

.. code-block:: yaml

  auth_address: 172.17.17.2

.. _configuration-options-auth-port:

``auth-port``
-------------

The port to listen on for incoming authorisation requests.

Default: ``49018``

CLI usgae example:

.. code-block:: bash

  $ napalm-logs --auth-port 2022

Configuration file example:

.. code-block:: yaml

  auth_port: 2022

.. _configuration-options-enable-metrics:

``enable-metrics``
------------------

.. versionadded:: 0.6.0

Enable metrics collection exposition (Prometheus metrics).

Default: ``false``

CLI usgae example:

.. code-block:: bash

  $ napalm-logs --enable-metrics

Configuration file example:

.. code-block:: yaml

  metrics_enabled: true

.. _configuration-options-metrics-address:

``metrics-address``
-------------------

.. versionadded:: 0.6.0

The IP address to use to listen for all incoming metrics requests. This is the
address that the Prometheus HTTP server exposes metrics from.

Default: ``0.0.0.0``.

CLI usage example:

.. code-block:: bash

  $ napalm-logs --metrics-address 172.17.17.1

Configuration file example:

.. code-block:: yaml

  metrics_address: 172.17.17.1

.. _configuration-options-metrics-port:

``metrics-port``
----------------

.. versionadded:: 0.6.0

The port to listen on for incoming metrics requests. This is the port that
the Prometheus HTTP server exposes metrics from.

Default: ``9443``

CLI usgae example:

.. code-block:: bash

  $ napalm-logs --metrics-port 2022

Configuration file example:

.. code-block:: yaml

  metrics_port: 2022

.. _configuration-options-metrics-dir:

``metrics-dir``
---------------

.. versionadded:: 0.6.0

The directory used by the processes for metrics collection. This directory must
be writable. If the directory does not exist, we attempt to create it.

Default: ``/tmp/napalm_logs_metrics``

CLI usgae example:

.. code-block:: bash

  $ napalm-logs --metrics-dir /tmp/a_new_dir_for_metrics

Configuration file example:

.. code-block:: yaml

  metrics_dir: /tmp/a_new_dir_for_metrics

.. _configuration-options-metrics-attrs:

``metrics_include_attributes``
------------------------------

.. versionadded:: 0.10.0

Disable detailed metrics with attributes per published device OS, hostname, and 
napalm-logs error type. Default: ``True`` (the metrics will include detailed 
attributes).

Configuration file example:

.. code-block:: yaml

  metrics_include_attributes: false

.. _configuration-options-certificate:

``certificate``
---------------

The certificate to use for the authorisation process. This will be presented to
incoming clients during the TLS handshake.

CLI usage example:

.. code-block:: bash

  $ napalm-logs --certificate /var/cache/server.crt

Configuration file example:

.. code-block:: yaml

  certificate: /var/cache/server.crt

.. _configuration-options-config-file:

``config-file``
---------------

Specifies the file where further configuration options can be found.

Default: ``/etc/napalm/logs``.

CLI usage example:

.. code-block:: bash

  $ napalm-logs -c /srv/napalm-logs
  $ napalm-logs --config-file /srv/napalm-logs

.. _configuration-options-config-path:

``config-path``
---------------

The directory path where device configuration files can be found. These are the
files that contain the syslog message format for each device.

CLI usage example:

.. code-block:: bash

  $ napalm-logs --config-path /home/admin/napalm-logs/

Configuration file example:

.. code-block:: yaml

  config_path: /home/admin/napalm-logs/

.. _configuration-options-device-worker-processes:

``device-worker-processes``: ``1``
----------------------------------

.. versionadded:: 0.3.0

This option configures the number of worker processes to be started for each
platform class. For better performances and higher capacity, it is recommended
to increase this number, which defaults to 1, i.e., by default there will be
started a single process per platform.

.. note::

    Increasing the number of processes, will imply higher memory consumption.

    For fine-tunning, consider increasing this number, and at the same time
    exclude (or include) the appropriate platforms, using the following options:
    :ref:`configuration-options-device-blacklist` and
    :ref:`configuration-options-device-whitelist`.

.. _configuration-options-disable-security:

``disable-security``
--------------------

If set no encryption or message signing will take place. All messages will be in
plain text. The client will not be able to verify that a message was generated
by the server.

**It is not recommended to use this in a production environment.**

CLI usage example:

.. code-block:: bash

  $ napalm-logs --disable-security

Configuration file example:

.. code-block:: yaml

  disable_security: true

.. note::

    Starting with release :ref:`release-0.4.0`, it is possible to specify 
    this option for each Publisher individually. See 
    :ref:`publisher-opts-disable-security`.

.. _configuration-options-extension-config-path:

``extension-config-path``
-------------------------

A path where you can specify further device configuration files that contain the
syslog message format for devices.

CLI usage example:

.. code-block:: bash

  $ napalm-logs --extension-config-path /home/admin/napalm-logs/

Configuration file example:

.. code-block:: yaml

  extension_config_path: /home/admin/napalm-logs/

.. _configuration-hwm:

``hwm``: 1000
-------------

.. versionadded:: 0.3.0

This option controls the ZeroMQ high water mark (the hard limit on the maximum
number of outstanding messages ZeromMQ shall queue in memory).
If this limit has been reached the internal sockets enter an exceptional state,
and ZeroMQ blocks the reception of further messages.
This option can be used to tune the performances of the napalm-logs, in terms of
total messages processed. While the default limit should be generally
enough, in environments with extremely high density of syslog messages to be
processed, it is recommended to increase this value. Keep in mind that a higher
queue implies higher memory consumption.
For maximum capacity, this option can be set to ``0``, i.e., inifinite queue.

CLI usage example:

.. code-block:: bash

  $ napalm-logs --hwm 0

Configuration file example:

.. code-block:: yaml

  hwm: 0

.. _configuration-backlog:

``backlog``: 100
-------------

.. versionadded:: 0.11.0

The zmq backlog option shall set the maximum length of the queue of outstanding peer 
connections for the specified socket; this only applies to connection-oriented transports.
This is used for both external zmq publishers but also but the internally defined zmq that 
saves the messages before sending them to the configured publishers.

This option can be used to tune the performances of the napalm-logs. 
While the default limit should be generally enough, in environments with extremely high 
density of syslog messages to be processed, it is recommended to increase this value.

CLI usage example:

.. code-block:: bash

  $ napalm-logs --backlog 0

Configuration file example:

.. code-block:: yaml

  backlog: 0

.. _configuration-options-keyfile:

``keyfile``
-----------

The private key for the certificate specified by the ``certificate`` option.
This will be used to generate a key to encrypt messages.

CLI usage example:

.. code-block:: bash

  $ napalm-logs --keyfile /var/cache/server.key

Configuration file example:

.. code-block:: yaml

  keyfile: /var/cache/server.key

.. _configuration-options-listener:

``listener``: ``udp``
---------------------

The module to use when listening for incoming syslog messages. For more details,
see :ref:`listener`.

Starting with the :ref:`release-0.4.0`, you are able to listen to
the syslog messages over multiple concomitant channels. This capability is
available only from the configuration file. For more configuration options for 
the listener interface, please check the :ref:`listener` section.

Default: ``udp``.

CLI usage example:

.. code-block:: bash

  $ napalm-logs --listener kafka

Configuration file example:

.. code-block:: yaml

  listener: kafka

Multiple listeners configuration example (file):

.. versionadded:: 0.4.0

.. code-block:: yaml

    listener:
      - kafka: {}
      - udp:
          address: 1.2.3.4
          port: 5514
          buffer_size: 2048
      - tcp:
          address: 1.2.3.4
          port: 5515

.. _configuration-options-log-file:

``log-file``
------------

The file where to send log messages.

If you want log messages to be outputted to the command line you can specify
``--log-file cli``.

Default: ``/var/log/napalm/logs``.

CLI usage example:

.. code-block:: bash

  $ napalm-logs --log-file /var/log/napalm-logs

Configuration file example:

.. code-block:: yaml

  log_file: /var/log/napalm-logs

.. _configuration-options-log-format:

``log-format``
--------------

The format of the log messages.

Default: ``%(asctime)s,%(msecs)03.0f [%(name)-17s][%(levelname)-8s] %(message)s``.

Example: ``2017-07-03 11:54:25,300,301 [napalm_logs.listener.tcp][INFO    ] Stopping listener process``

CLI usage example:

.. code-block:: bash

  $ napalm-logs --log-format '%(asctime)s,%(msecs)03.0f [%(levelname)] %(message)s'

Configuration file example:

.. code-block:: yaml

  log_format: '%(asctime)s,%(msecs)03.0f [%(levelname)] %(message)s'

.. _configuration-options-log-level:

``log-level``: ``WARNING``
--------------------------

The level at which to log messages. Possible options are ``CRITIAL``, ``ERROR``,
``WARNING``, ``INFO``, ``DEBUG``.

Default: ``WARNING``.

CLI usage example:

.. code-block:: bash

  $ napalm-logs -l debug
  $ napalm-logs --log-level info

Configuration file example:

.. code-block:: yaml

  log_level: info

.. _configuration-options-port:

``port``: ``514``
-----------------

The port to use to listen for all incoming syslog messages. This can be
assigned using the CLI argument ``-p``. When working with multiple listeners, 
it is recommended to specify the ``port`` argument for each listener to avoid
confusions.

Default: ``514``.

CLI usage example:

 code-block:: bash

  $ napalm-logs -p 1024
  $ napalm-logs --port 1024

Configuration file example:

.. code-block:: yaml

  port: 1024

.. _configuration-options-publisher:

``publisher``: ``zmq``
----------------------

The channel(s) to be used when publishing the structured napalm-logs documents.
Starting with :ref:`release-0.4.0`, it is possible to publish the
messages over multiple channels. Each publisher has it's separate set of 
configuration options, for more details see :ref:`publisher`.

Default: ``zmq`` (ZeroMQ)

CLI usage example:

.. code-block:: bash

    $ napalm-logs --publisher zmq

Configuration file example:

.. code-block:: yaml

    publisher: zmq

Multiple publishers configuration example (file):

.. versionadded:: 0.4.0

.. code-block:: yaml

    publisher:
      - zmq:
          address: 1.2.3.4
          port: 1234
      - kafka:
          bootstrap_servers:
            - kk1.brokers.example.org
            - 192.168.0.1
            - 192.168.0.2:5678
          topic: napalm-logs-out
      - http:
          address: https://example.com/webhook

.. _configuration-options-publish-address:

``publish-address``: ``0.0.0.0``
--------------------------------

The IP address to use to output the processed message. When publishing the 
structured napalm-logs documents over multiple transports, it is recommended to 
specify the ``address`` field per publisher. For more examples, see 
:ref:`configuration-options-publisher` and :ref:`publisher`.

Default: ``0.0.0.0``.

CLI usage example:

.. code-block:: bash

  $ napalm-logs --publish-address 172.17.17.3

Configuration file example:

.. code-block:: yaml

  publish_address: 172.17.17.3

.. _configuration-options-publish-port:

``publish-port``: ``49017``
---------------------------

The port to use to output the processes message. When publishing the structured 
napalm-logs documents over multiple transports, it is recommended to specify 
the ``port`` field per publisher. For more examples, see 
:ref:`configuration-options-publisher` and :ref:`publisher`.

Default: ``49017``.

CLI usage example:

.. code-block:: bash

  $ napalm-logs --publish-port 2048

Configuration file example:

.. code-block:: yaml

  publish_port: 2048

.. _configuration-options-serializer:

``serializer``: ``msgpack``
---------------------------

The name of the serializer to be used when publishing the napalm-logs 
structured documents. When working with multiple publishers it is possible to 
control their serialization method individually, using the
:ref:`publisher-opts-serializer` option.

Default: ``msgpack``

CLI Example:

.. code-block:: bash

    $ napalm-logs -s json
    $ napalm-logs --serializer yaml

Configuration file example:

.. code-block:: yaml

    serializer: json

.. _configuration-options-transport:

``transport``: ``zmq``
----------------------

The module to use to output the processed message information. For more details,
see :ref:`publisher`.

.. warning::

    This option is no longer supported as of :ref:`release-0.4.0`. Use 
    :ref:`configuration-options-publisher` instead.

Default: ``zmq`` (ZeroMQ).

CLI usage example:

.. code-block:: bash

  $ napalm-logs -t kafka
  $ napalm-logs --transport kafka

Configuration file example:

.. code-block:: yaml

  transport: kafka

Or:

.. code-block:: yaml

  transport: kafka

Config File Only Options
++++++++++++++++++++++++

The options to be used inside of the pluggable modules are not provided via the
command line, they need to be provided in the config file.

.. _configuration-options-device-whitelist:

``device_whitelist``
--------------------

List of platforms to be supported. By default this is an empty list, thus
everything will be accepted. This is useful to control the number of
sub-processes started.

Example:

.. code-block:: yaml

  device_whitelist:
    - junos
    - iosxr

.. _configuration-options-device-blacklist:

``device_blacklist``
--------------------

List of platforms to be ignored. By default this list is empty, thus nothing
will be ignored. This is also useful to control the number of sub-processes
started.

Example:

.. code-block:: yaml

  device_blacklist:
    - eos

.. _configuration-options-sentry-dsn:

``sentry_dsn``
--------------

.. versionadded:: 0.11.0

The Sentry DSN to identify the project to send traces to.

Example:

.. code-block:: yaml

  sentry_dsn: https://187deccf24d5ea7dc:f3e690bd3a03fb@sentry.example.com/777

.. _configuration-options-sentry-opts:

``sentry_opts``
---------------

.. versionadded:: 0.11.0

Dictionary of Sentry options to customise the behaviour of traces reports. See
https://docs.sentry.io/platforms/python/configuration/options/ for more 
details. By default, ``traces_sample_rate`` is set to 1.0 (100%).

Example:

.. code-block:: yaml

  sentry_opts:
    traces_sample_rate: 0.5
    sample_rate: 0.1
    max_breadcrumbs: 30
