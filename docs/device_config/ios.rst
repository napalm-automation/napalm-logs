.. _device-configuration-ios:

=========
Cisco IOS
=========

The following will configure IOS to send the syslog messages, over UDP, to the
IP Address ``10.10.10.1``, port 10101:


.. code-block:: text

    logging host 10.10.10.1 transport udp port 10101

To correctly send the hostname information, is is also recommended to explicitly
configure the following:

.. code-block:: text

    logging origin-id hostname

Otherwise the device won't send this information.
