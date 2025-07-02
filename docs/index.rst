===========
Napalm-logs
===========

Python library to parse syslog messages from network devices and produce JSON
serializable Python objects, in a vendor agnostic shape. The output objects are
structured following the `OpenConfig <http://www.openconfig.net/>`_ or
`IETF <https://github.com/YangModels/yang/tree/master/standard/ietf>`_ YANG models.

For example, the following syslog message from a Juniper device:

.. code-block:: text

	<149>Jun 21 14:03:12  vmx01 rpd[2902]: BGP_PREFIX_THRESH_EXCEEDED: 192.168.140.254 (External AS 4230): Configured maximum prefix-limit threshold(140) exceeded for inet4-unicast nlri: 141 (instance master) 

Will produce the following object:

.. code-block:: json

    {
      "yang_message": {
        "bgp": {
          "neighbors": {
            "neighbor": {
              "192.168.140.254": {
                "state": {
                  "peer_as": "4230"
                },
                "afi_safis": {
                  "afi_safi": {
                    "inet4": {
                      "state": {
                        "prefixes": {
                          "received": 141
                        }
                      },
                      "ipv4_unicast": {
                        "prefix_limit": {
                          "state": {
                            "max_prefixes": 140
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      },
      "message_details": {
        "processId": "2902",
        "severity": 5,
        "facility": 18,
        "hostPrefix": null,
        "pri": "149",
        "processName": "rpd",
        "host": "vmx01",
        "tag": "BGP_PREFIX_THRESH_EXCEEDED",
        "time": "14:03:12",
        "date": "Jun 21",
        "message": "192.168.140.254 (External AS 4230): Configured maximum prefix-limit threshold(140) exceeded for inet4-unicast nlri: 141 (instance master)"
      },
      "timestamp": 1498053792,
      "facility": 18,
      "ip": "127.0.0.1",
      "host": "vmx01",
      "yang_model": "openconfig-bgp",
      "error": "BGP_PREFIX_THRESH_EXCEEDED",
      "os": "junos",
      "severity": 5
    }

The library is provided with a command line program which acts as a daemon,
running in background and listening to syslog messages continuously, then
publishing them over secured channels, where multiple clients can subscribe.

It is flexible to listen to the syslog messages via UDP or TCP, but also from
brokers such as Apache Kafka. Similarly, the output objects can be published via
various channels such as ZeroMQ, Kafka, or remote server logging. It is also
pluggable enough to extend these capabilities and listen or publish to other
services, depending on the needs.

The messages are published over a secured channel, encrypted and signed.
Although the security can be disabled, this is highly discouraged.

Output data
-----------

The objects published by napalm-logs are structured data, with the hierarchy
standardized in the OpenConfig and IETF models. To check what models are used for
each message type, together with examples of raw syslog messages and sample
output objects, please check the :ref:`messages` section.

Install
-------

napalm-logs is available on PyPi and can easily be installed using the following
command:

.. code-block:: bash

    $ pip install napalm-logs

For advanced installation notes, see :ref:`installation`.

How to use napalm-logs
----------------------

Basic Configuration
+++++++++++++++++++

Firstly you need to decide if you would like all messages between *napalm-logs*
and the clients to be encrypted. If you do want them to be encrypted you will
require a certificate and key, which you can generate using the following
command:

.. code-block:: bash

    openssl req -nodes -x509 -newkey rsa:4096 -keyout /var/cache/napalm-logs.key -out /var/cache/napalm-logs.crt -days 365

This will provide a self-signed certificate ``napalm-logs.crt`` and key
``napalm-logs.key`` under the ``/var/cache`` directory.

If you do not require the messages to be encrypted you can ignore the above
step and just use the command line argument ``--disable-security`` when starting
*napalm-logs*.

Each of the other config options come with defaults, so you can now start
*napalm-logs* with default options and your chosen security options.

Starting napalm-logs
++++++++++++++++++++

*Napalm-logs* will need to be run with root privileges if you want it to be able
to listen on ``udp`` port ``514`` - the standard syslog port. If you need to
run it via sudo and it has been installed in a virtual env, you will need to
include the full path. In these examples I will run as root.

To start napalm-logs using the crt and key generated above you should run the
following command:

.. code-block:: bash

    napalm-logs --certificate /var/cache/napalm-logs.crt --keyfile /var/cache/napalm-logs.key

This will start napalm-logs listening for incoming syslog messages on
``0.0.0.0`` port ``514``. It will also start to listen for incoming client
requests on ``0.0.0.0`` port ``49017``, and incoming authentication requests on
``0.0.0.0`` port ``49018``.
For more information on authentication please see the :ref:`authentication`
section.

Further Configuration
+++++++++++++++++++++

It is possible to change the address and ports that napalm-logs will use, let's
take a look at these options:

.. code-block:: bash

	  -a ADDRESS, --address=ADDRESS
							Listener address. Default: 0.0.0.0
	  -p PORT, --port=PORT  Listener bind port. Default: 514
	  --publish-address=PUBLISH_ADDRESS
							Publisher bind address. Default: 0.0.0.0
	  --publish-port=PUBLISH_PORT
							Publisher bind port. Default: 49017
	  --auth-address=AUTH_ADDRESS
							Authenticator bind address. Default: 0.0.0.0
	  --auth-port=AUTH_PORT
							Authenticator bind port. Default: 49018

There are several ``plugable`` parts to napalm-logs, two of which are the
``listener`` and the ``publisher``. The listener is the part that ingests the
incoming syslog messages, and the publisher is the part that outputs them to the
client.

You can chose which listener to use, and which publisher to use by using the
following arguments:

.. code-block:: bash

	  --listener=LISTENER   Listener type. Default: udp
	  -t TRANSPORT, --transport=TRANSPORT
							Publish transport. Default: zmq

There are more configuration options, please see :ref:`configuration-options`
for more details.

Configuration file example
++++++++++++++++++++++++++

The napalm-logs server can be started without any CLI aguments, as long as they
are correctly specified under the configuration file. The default path of the
configuration file is under ``/etc/napalm/logs``. To select a different
filepath, we can use the ``-c`` option:

.. code-block:: bash

	napalm-logs -c /home/admin/napalm/logs

The configuration file is formatted as YAML, which makes it more human readable.
In general, any configuration option available on the CLI can be specified in
the configuration file, with the mention that hyphen is replaced by underscore,
e.g.: the CLI option ``auth-address`` becomes ``auth_address`` in the
*napalm-logs* configuration file.

.. code-block:: yaml

    address: 172.17.17.1
    port: 5514
    publish_address: 172.17.17.2
    publish_port: 49017
    transport: zmq
    listener:
      kafka:
        bootstrap_servers:
          - 10.10.10.1
          - 10.10.10.2
          - 10.10.10.3
        opts:
          batch_size: 16384
          max_request_size: 1048576
          buffer_memory: 33554432
          send_buffer_bytes: 131072
          max_in_flight_requests_per_connection: 5
          retries: 0
          max_block_ms: 60000
          linger_ms: 1000

The configuration above listens to the syslog messages from the Kafka bootstrap
servers ``10.10.10.1``, ``10.10.10.2`` and ``10.10.10.3`` then publishes the
structured objects encrypted and serialized via ZeroMQ, serving them at the
address ``172.17.17.2``, port ``49017``.

The opts listed there are the kafka producer options that the napalm-logs exposes
They are directly named in the same way as the kafka python3 package:
https://kafka-python.readthedocs.io/en/master/apidoc/KafkaProducer.html
These opts are optional - you can chose to add them completely, only partially or not at all.

Check the complete list of configuration options under
:ref:`configuration-options`.

Starting a Client
+++++++++++++++++

The client structure depends on how you start the napalm-logs daemon. If the
security is disabled (via the CLI option ``--disable-security`` or through the
configuration file, where the ``disable_security`` field is set as ``false``),
the client script is as simple as:

.. code-block:: python

    #!/usr/bin/env python

    import zmq
    import napalm_logs.utils

    server_address = '127.0.0.1'
    server_port = 49017

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect('tcp://{address}:{port}'.format(address=server_address,
                                                   port=server_port))
    socket.setsockopt(zmq.SUBSCRIBE, '')

    while True:
        raw_object = socket.recv()
        print(napalm_logs.utils.unserialize(raw_object))

Which subscribes to the ZeroMQ bus and deserializes messages using the
``napalm_logs.utils.unserialise`` helper. The ``server_address`` and the
``server_port`` of the client represent the ``--publish-address`` and the
``--publish-port`` of the napalm-logs daemon.

When the program is started with security enabled (**recommended**), the
clients can use the ``napalm_logs.utils.ClientAuth`` class, which executes the
handshake to retrieve the encryption key and hex of the verification key. This
class requires the certificate (the same certificate specified when starting
the napalm-logs daemon), as well as the authentication address and port
(corresponding to the ``--auth-address`` and ``--auth-port`` CLI arguments or
``auth_address`` and ``auth_port`` configuration fields sent to the napalm-logs
daemon):

.. code-block:: python

	#!/usr/bin/env python

	import napalm_logs.utils
	import zmq

	server_address = '127.0.0.1'
	server_port = 49017
	auth_address = '127.0.0.1'
	auth_port = 49018

	certificate = '/var/cache/napalm-logs.crt' # This is the server crt generated earlier

	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	socket.connect('tcp://{address}:{port}'.format(address=server_address,
	                                               port=server_port))
	socket.setsockopt(zmq.SUBSCRIBE, '')

	auth = napalm_logs.utils.ClientAuth(certificate,
	                                    address=auth_address,
	                                    port=auth_port)

	while True:
	    raw_object = socket.recv()
	    decrypted = auth.decrypt(raw_object)
	    print(decrypted)


.. toctree::
   :maxdepth: 1

   installation/index
   docker/index
   device_config/index
   options/index
   clients/index
   messages/index
   metrics/index
   authentication/index
   listener/index
   publisher/index
   serializer/index
   logger/index
   buffer/index
   syslog/index
   developers/index
   releases/index
