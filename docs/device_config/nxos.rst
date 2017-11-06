.. _device-configuration-nxos:

===========
Cisco NX-OS
===========

The following will configure NX-OS to send the syslog messages, over UDP, to the
IP Address ``10.10.10.1``, port 10101:

.. code-block::

    logging server 10.10.10.1 port 10101
