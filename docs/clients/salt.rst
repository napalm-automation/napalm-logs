.. _clients-salt:

====
Salt
====

The structured messages published by napalm-logs can be imported into the Salt
event bus using the `napalm-logs Engine <https://docs.saltstack.com/en/latest/ref/engines/all/salt.engines.napalm_syslog.html>`_ introduced in the `2017.7 release (Nitrogen) <https://docs.saltstack.com/en/latest/topics/releases/2017.7.0.html#network-automation>`_.

Configuration
-------------

The ``address`` and ``port`` fields on the napalm-syslog Salt engine side must
correspond to the values configured for :ref:`configuration-options-publish-address`
and :ref:`configuration-options-publish-address` on the napalm-logs side.
Similarly, ``auth_address``, ``auth_port``, ``certificate``, and ``transport``
would have the values specified for :ref:`configuration-options-auth-address`
and :ref:`configuration-options-auth-port`,
:ref:`configuration-options-certificate`, and
:ref:`configuration-options-transport`.

.. note::

  Do not conflate the ``address`` and the ``port`` arguments on the napalm-logs
  side with ``address`` and ``port`` napalm-syslog Salt Engine fields: they are
  *not* the same!

For more configuration options and usage examples of the napalm-syslog Salt
Egine, please check the `documentation <https://docs.saltstack.com/en/latest/ref/engines/all/salt.engines.napalm_syslog.html>`_.

Configuration example:

When the napalm-logs engine is started usign the command line ``$ napalm-logs -a 1.2.3.4 -p 1234 --publish-address 5.6.7.8 --publish-port 5678 --disable-security``,
or using the configuration file:

.. code-block:: yaml

    address: 1.2.3.4
    port: 1234
    publish_address: 5.6.7.8
    publish_port: 5678

The napalm-syslog engine is configured under the Salt Master or Minion:

.. code-block:: yaml

  engines:
    - napalm_syslog:
        transport: zmq
        address: 5.6.7.8
        port: 5678
        disable_security: true
