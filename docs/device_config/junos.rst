.. _device-configuration-junos:

=====
Junos
=====

The following will configure Junos to send the syslog messages, over UDP, to the
IP Address ``10.10.10.1``, port 10101:


.. code-block::

    set system syslog host 10.10.10.1 port 10101 any any
