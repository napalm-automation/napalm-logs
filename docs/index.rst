===========
Napalm-logs
===========
Python library to parse syslog messages

Install
-------
napalm-logs is available on PyPi and can easily be installed using the following command:

.. code-block:: bash

    pip install napalm-logs

How to use napalm-logs
----------------------
Basic Configuration
+++++++++++++++++++
Firstly you need to decide if you would like all messages between napalm-logs and the clients to be encrypted.

If you do want them to be encrypted you will require a certificate and key, which you can generate using the following command:

.. code-block:: bash

    openssl req -nodes -x509 -newkey rsa:4096 -keyout napalm-logs.key -out napalm-logs.crt -days 365

This will provide a self-signed certificate ``napalm-logs.crt`` and key ``napalm-logs.key``

If you do not require the messages to be encrypted you can ignore the above step and just use the command line argument ``--disable-security`` when starting napalm-logs.

Each of the other config options come with defaults, so you can now start napalm-logs with default options and your chosen security options.

Starting napalm-logs
++++++++++++++++++++
Napalm-logs will need to be run with root privileges if you want it to be able to listen on ``udp`` port ``514`` - the standard syslog port. If you need to run it via sudo and it has been installed in a virtual env, you will need to include the full path. In these examples I will run as root.

To start napalm-logs using the crt and key generated above you should run the following command:

.. code-block:: bash

    napalm-logs --certificate napalm-logs.crt --keyfile napalm-logs.key

This will start napalm-logs listening for incoming syslog messages on ``0.0.0.0`` port ``514``. It will also start to listen for incoming client requests on ``0.0.0.0`` port ``49017``, and incoming authentication requests on ``0.0.0.0`` port ``49018``. For more information on authentication please see the authentication section.

Further Configuration
+++++++++++++++++++++

It is possible to change the address and ports that napalm-logs will use, lets take a look at these options:

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

There are several ``plugable`` parts to napalm-logs, two of which are the ``listener`` and the ``publisher``. The listener is the part that ingests the incoming syslog messages, and the publisher is the part that outputs them to the client.

You can chose which listener to use, and which publisher to use by using the following arguments:

.. code-block:: bash

	  --listener=LISTENER   Listener type. Default: udp
	  -t TRANSPORT, --transport=TRANSPORT
							Publish transport. Default: zmq

There are more configuration options, please see relevant sections for more details.

Starting a Client
+++++++++++++++++

Here is the basic code you would need for a client:

.. code-block:: python

	#!/usr/bin/env python

	import napalm_logs.utils
	import zmq

	server_address = '127.0.0.1'
	server_port = 49017
	auth_address = '127.0.0.1'
	auth_port = 49018

	certificate = 'napalm-logs.crt' # This is the server crt generated earlier

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
	    print decrypted


.. toctree::
   :maxdepth: 2

   installation/index
   options/index
   developers/index
