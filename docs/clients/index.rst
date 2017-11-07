.. _clients:

=======
Clients
=======

The messages published by napalm-logs can be used in a variety of applications,
as there are no restrictions regarding the channel (see :ref:`publisher`).

The capabilities are already embedded in well known :ref:`clients-frameworks`,
or the user can consume the structured messages using custom
:ref:`clients-scripts`.

.. _clients-frameworks:

Frameworks
^^^^^^^^^^

.. toctree::
   :maxdepth: 1

   salt
   stackstorm

.. _clients-scripts:

Example Scripts
^^^^^^^^^^^^^^^

For simplicity, the examples below assume that napalm-logs is started using
:ref:`--disable-security <configuration-options-disable-security>`, and
:ref:`publisher-zmq` is used as publisher.

.. _clients-scripts-python:

Python
------

Receive the messages from napalm-logs and print on the command line:

.. code-block:: python

    import zmq
    import napalm_logs.utils

    server_address = '127.0.0.1'  # --publish-address
    server_port = 49017           # --publish-port

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect('tcp://{address}:{port}'.format(address=server_address,
                                                   port=server_port))
    socket.setsockopt(zmq.SUBSCRIBE, '')

    while True:
        raw_object = socket.recv()
        print(napalm_logs.utils.unserialize(raw_object))

.. _clients-scripts-nodejs:

JavaScript (Node.js)
--------------------

Receive the napalm-logs messages into a Node.js app, which only logs on the
console. This assumes `zeromq.js <https://github.com/zeromq/zeromq.js/>`_ and
`msgpack-lite <https://github.com/kawanet/msgpack-lite>`_ bindings are installed
(``npm install zeromq`` and ``npm install msgpack-lite``).

.. code-block:: javascript

    var zmq = require('zeromq')
    var msgpack = require('msgpack-lite');
    var sock = zmq.socket('sub');
    sock.connect('tcp://127.0.0.1:49017');
    sock.subscribe('');
    sock.on('message', function(msg){
        var data = msgpack.decode(msg);
        console.log('Received message:');
        console.log(data);
    });
