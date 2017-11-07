.. _device-configuration-eos:

==========
Arista EOS
==========

The following will configure EOS to send the syslog messages, over UDP, to the
IP Address ``10.10.10.1``, port 10101:

.. code-block:: text

    logging host 10.10.10.1 10101

To correctly send the hostname information, is is also recommended to explicitly
configure the following:

.. code-block:: text

    logging format hostname fqdn
