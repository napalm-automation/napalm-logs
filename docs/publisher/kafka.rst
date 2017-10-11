.. _publisher-kafka:

=====
Kafka
=====

Submit structured messages to Apache Kafka.

.. code-block:: bash

  $ sudo napalm-logs --publisher kafka

Available options:

.. _publisher-opts-bootstrap-servers:

``bootstrap_servers``
---------------------

``host[:port]`` string (or list of ``host[:port]`` strings) that the consumer
should contact to bootstrap initial cluster metadata. This does not have to be
the full node list. It just needs to have at least one broker that will respond
to a Metadata API Request.

Example:

.. code-block:: yaml

  publisher:
    kafka:
      bootstrap_servers:
        - kk1.brokers.example.org
        - kk1.brokers.example.org:1234
        - 192.168.0.1
        - 192.168.0.2:5678

.. _publisher-opts-kafka-topic:

``topic``: ``napalm-logs``
--------------------------

The Kafka topic to use when publishing messages.

Example:

.. code-block:: yaml

  publisher:
    kafka:
      topic: napalm-logs-out
