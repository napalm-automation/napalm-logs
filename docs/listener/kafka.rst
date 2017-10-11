.. _listener-kafka:

=====
Kafka
=====

Receive unstructured syslog messages from Apache Kafka.

Available options:

``bootstrap_servers``
---------------------

``host[:port]`` string (or list of ``host[:port]`` strings) that the consumer
should contact to bootstrap initial cluster metadata. This does not have to be
the full node list. It just needs to have at least one broker that will respond
to a Metadata API Request.

Example:

.. code-block:: yaml

  listener:
    kafka:
      bootstrap_servers:
        - kk1.brokers.example.org
        - kk1.brokers.example.org:1234
        - 192.168.0.1
        - 192.168.0.2:5678

.. code-block:: yaml

  listener:
    kafka:
      bootstrap_servers: kk1.brokers.example.org:1234

``group_id``: ``napalm-logs``
-----------------------------

The bootstrap servers group ID name.

Example:

.. code-block:: yaml

  listener:
    kafka:
      group_id: napalm-logs-servers

``topic``: ``syslog.net``
-------------------------

The topic to subscribe to and receive messages from.

Example:

.. code-block:: yaml

  listener:
    kafka:
      topic: napalm-logs-in
