.. _device-configuration-iosxr:

============
Cisco IOS-XR
============

The following will configure IOS-XR to send the syslog messages, over UDP, to the
IP Address ``10.10.10.1``, port 10101:


.. code-block::

    logging 10.10.10.1 port 10101

To correctly send the hostname information, is is also recommended to explicitly
configure the following:

.. code-block::

    logging hostnameprefix <hostname of the device>

Otherwise the device won't send this information.
