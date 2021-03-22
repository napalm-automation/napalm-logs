.. _listener-tcp:

===
TCP
===

Receive the unstructured syslog messages over TCP.

Available options:

.. _listener-tcp-buffer-size:

``buffer_size``: ``1024``
-------------------------

The socket buffer size, in bytes.

Example:

.. code-block:: yaml

  listener:
    tcp:
      buffer_size: 2048


.. _listener-tcp-reuse-port:

``reuse_port``: ``false``
-------------------------

.. versionadded:: 0.6.0

Enable or disable ``SO_REUSEPORT`` on listener's socket.

Example:

.. code-block:: yaml

  listener:
    tcp:
      reuse_port: true


.. _listener-tcp-socket-timeout:

``socket_timeout``: ``60``
--------------------------

The socket timeout, in seconds.

Example:

.. code-block:: yaml

  listener:
    tcp:
      socket_timeout: 5


.. _listener-tcp-max-clients:

``max_clients``: ``5``
----------------------

The maximum number of parallel connections to accept.

Example:

.. code-block:: yaml

  listener:
    tcp:
      max_clients: 100

.. _listener-tcp-framing:

``framing``: ``traditional``
----------------------------

.. versionadded:: 0.10.0

Framing mode used when receiving messages. Available options: ``traditional`` 
or ``octet-counted``.

In protocol engineering, *framing* means how multiple messages over the same
connection are separated. Usually, this is transparent to users. Unfortunately,
the early syslog protocol evolved and so there are cases where users need to
specify the framing. The ``traditional`` framing is nontransparent. With it,
messages end when an LF (i.e., line break / return) is encountered, and the next
message starts immediately after the LF. If multi-line messages are received,
these are essentially broken up into multiple message, usually with all but the
first message segment being incorrectly formatted. The ``octet-counted`` framing
solves this issue. With it, each message is prefixed with the actual message
length, so that a receiver knows exactly where the message ends. Multi-line
messages cause no problem here. This mode is very close to the method described
in RFC5425 for TLS-enabled syslog. Unfortunately, only few syslogd
implementations support ``octet-counted`` framing. As such, the ``traditional``
framing is set as default, even though it has defects. If it is known that the
transmitter supports ``octet-counted`` framing, it is suggested to use that
framing mode.

(Detailed documentation notes based on `<rsyslog 
omfwd> https://www.rsyslog.com/doc/v8-stable/configuration/modules/omfwd.html#tcp-framing`__)

.. _listener-tcp-frame-delimiter:

``frame_delimiter``: ``\n``
---------------------------

.. versionadded:: 0.10.0

Sets a custom frame delimiter for TCP transmission when ``framing`` is
configured in ``traditional`` mode. The delimiter has to be a number between
0 and 255 (representing the ASCII-code of said character). The default value for
this parameter is 10, representing a ``\n``.
