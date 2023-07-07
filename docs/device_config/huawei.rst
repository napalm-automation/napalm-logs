.. _device-configuration-huawei:

==========
Huawei VRP
==========

.. versionadded:: 0.6.0

The following will configure Huawei VRP to send the syslog messages, over UDP, to the
IP Address ``10.10.10.1``

.. code-block:: text

    info-center loghost 10.10.10.1

The following configuration is also required on the device for napalm-logs to match
incoming logs

.. code-block:: text

    info-center timestamp log format-date precision-time millisecond
