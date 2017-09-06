.. _authentication:

=====================
Client Authentication
=====================

With the event-driven automation in mind, napalm-logs has been designed to be
safe and securely publish the outgoing messages. As these messages may trigger
automatic configurationc changes, or simply notifications, we must ensure their
authenticity. For these reasons, napalm-logs encrypts and signs the outgoing
messages.

Although highly discouraged, the user has the possibility to disable the
security at their own risk.

Whether the security is enabled or disabled, the messages published are binary
serialized using `MessagePack <http://msgpack.org/>`_.

The clients that connect to the publisher interface (see :ref:`publisher`), have
to retrieve the encryption and the signing key from the napalm-logs daemon.
In the core architecture of napalm-logs, when the security is not turned
off, another separate process is started, which listens to connections and
exchanges the keys with the client. The exchange is realised over a secure SSL
socket, using the certificate and the key configured when starting the daemon
(see :ref:`configuration-options-certificate` and
:ref:`configuration-options-keyfile`).
The authentication subsystem listens on a socket, whose configuration details
can be set using the :ref:`configuration-options-auth-address` and
:ref:`configuration-options-auth-port` options (either from the CLI, or in the
configuration file).

The client, before being able to decrypt the messages received from the
napalm-logs publisher, must receive the keys from the authenticator sub-system.

In order to ease the authentication process on the client side, we have included
a couple of helpers, making the key exchange and decryption easy:

.. code-block:: python

    #!/usr/bin/env python

    import zmq  # when using the ZeroMQ publisher
    import napalm_logs.utils

    server_address = '127.0.0.1'  # IP
    server_port = 49017           # Port for the napalm-logs publisher interface
    auth_address = '127.0.0.1'    # IP
    auth_port = 49018             # Port for the authentication interface

    certificate = '/var/cache/napalm-logs.crt' # This is the server crt generated earlier

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect('tcp://{address}:{port}'.format(address=server_address,
                                                   port=server_port))
    socket.setsockopt(zmq.SUBSCRIBE, '')  # subscribe to the napalm-logs publisher

    auth = napalm_logs.utils.ClientAuth(certificate,
                                        address=auth_address,
                                        port=auth_port)  # authenticate to napalm-logs

    while True:
        raw_object = socket.recv()  # receive the encrypted object
        decrypted = auth.decrypt(raw_object)  # check the siganture, decrypt and deserialize
        print(decrypted)

When the security is disabled, the clients no longer need to authenticate and
receive the keys, however they need to bear in mind to deserialize the messages.
We have also included a helper for that: ``napalm_logs.utils.unserialize``, see
the example below:

.. code-block:: python

    #!/usr/bin/env python

    import zmq  # when using the ZeroMQ publisher
    import napalm_logs.utils

    server_address = '127.0.0.1'  # IP
    server_port = 49017           # Port for the napalm-logs publisher interface

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect('tcp://{address}:{port}'.format(address=server_address,
                                                   port=server_port))
    socket.setsockopt(zmq.SUBSCRIBE, '')  # subscribe to the napalm-logs publisher

    while True:
        raw_object = socket.recv()  # binary object
        print(napalm_logs.utils.unserialize(raw_object))  # deserialize
