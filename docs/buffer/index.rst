.. _buffer:

================
Buffer Interface
================

.. versionadded:: 0.7.0

By design, syslog messages can be fired spuriously, and the same information 
may be sent multiple times within a short period of time. For example, when
an NTP server is unreachable, Junos would send the following message several
times from the same device, within just a couple of seconds:

.. code-block:: text

  Aug 27 12:03:46  router1 xntpd[4308]: NTP Server 10.10.10.1 is Unreachable
  Aug 27 12:03:47  router1 xntpd[4308]: NTP Server 10.10.10.1 is Unreachable
  Aug 27 12:03:49  router1 xntpd[4308]: NTP Server 10.10.10.1 is Unreachable

To ensure ``napalm-logs`` is sending notifications only for one copy of these
messages, you can enable the buffer interface to cache the first occurrence of
the message, and the next ones would not be published.

.. warning::

    Before enabling this feature please consider the caveats and the 
    limitations added by the interface of choice.
    One of the most important is the fact that lookups are time consuming and 
    might decrease the performances, and/or require a higher memory 
    consumption.

The Buffer interface is pluggable subsystem and can be enabled from the 
configuration file, under the ``buffer`` block, for example:

.. code-block:: yaml

  buffer:
    redis:
      host: 127.0.0.1
      db: 4

.. _buffer-drivers:

Available Buffer drivers and their options
------------------------------------------

.. toctree::
   :maxdepth: 1

   memory
   redis

Globally available options
--------------------------

In addition to the particular options for each individual Buffer driver, you
can fine tune ``napalm-logs`` using the following options:

.. _buffer-opts-expire-time:

``expire_time``: ``5``
-----------------------

The time in seconds to cache the message and filter out duplicates. The first 
occurrence of the message is recorded and hashed into the Buffer interface of 
choice. The next messages with the same content and looked up and discarded if 
they have been fired within ``expire_time`` seconds.

Configuration example:

.. code-block:: yaml

  buffer:
    mem:
      expire_time: 30
