.. _installation:

============
Installation
============

Creating a Virtualenv
+++++++++++++++++++++

It is recommended to install all the modules required for a new program into a
*Virtual Environment*. This ensures that the project dependencies are kept in
its own environment, making sure that you don't have any versioning issues when
other programs have the same dependencies.

.. code-block:: bash

    virtualenv napalm-logs

This will create a directory called ``napalm-logs`` in the directory that you
are currently in.

Now you need to activate the virtualenv:

.. code-block:: bash

    source napalm-logs/bin/activate

Installing Napalm-logs
++++++++++++++++++++++

Now install napalm-logs using pip:

.. code-block:: bash

    pip install napalm-logs

Docker
++++++++++++++++++++++

Napalm-logs can also be deployed via a Docker container.

`A Dockerfile has been made available in the GitHub repository <https://github.com/napalm-automation/napalm-logs/tree/master/docker>`_ allowing the configuration of the container to be customized.

Alternatively, `a pre-built image is available on Docker Hub <https://hub.docker.com/r/nathancatania/napalm-logs/>`_ which uses the UDP listener and publishes to Kafka by default.
The pre-built image is recommended for testing only as Napalm-logs is executed with security disabled by default.

Usage:

.. code-block:: bash

    docker run -d -p 6000:514/udp -i nathancatania/napalm-logs:latest

The above command will run the Napalm-logs container and listen on port 6000 (UDP) for incoming messages. By default, the pre-built container attempts to connect to a Kafka broker located at `127.0.0.1:9092` and will publish data to the `syslog.net` topic.

These defaults can be changed by specifying ENV variables at container runtime. For example:

.. code-block:: bash

    docker run -d -e KAFKA_BROKER_HOST=192.168.1.200 -e KAFKA_BROKER_PORT=9094 -e KAFKA_TOPIC=my_topic -p 55555:514/udp -i nathancatania/napalm-logs:latest

In this example:

* The container will listen on port 55555 for incoming messages.
* Napalm-logs will connect to a Kafka broker located at `192.168.1.200:9094`.
* Data will be published to the Kafka topic `my_topic`.

A list of available variables which can be changed is included below:

.. code-block:: yaml

    PUBLISH_PORT: 49017              # Source port of the host to publish data to Kafka on
    KAFKA_BROKER_HOST: 127.0.0.1     # Hostname or IP of the Kafka broker to publish to
    KAFKA_BROKER_PORT: 9092          # Port of the Kafka broker to publish to
    KAFKA_TOPIC: syslog.net          # The Kafka topic to push data to.
    SEND_RAW: true                   # Publish messages where the OS, but NOT the message could be identified.
    SEND_UNKNOWN: false              # Publish messages where both OS and message could not be identified.
    WORKER_PROCESSES: 1              # Increasing this increases memory consumption but is better for higher loads.
