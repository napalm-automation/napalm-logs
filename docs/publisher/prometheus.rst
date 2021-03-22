.. _publisher-prometheus:

==========
Prometheus
==========

.. versionadded:: 0.10.0

Expose *napalm-logs* notifications as Prometheus metrics.

.. important::

    In order to make use of this Publisher, you'll need to enable the 
    :ref:`configuration-options-enable-metrics` option (and eventually 
    customise the other related settings).

The metrics start with ``napalm_logs``, plus the *napalm-logs* notification 
name. For example, the metric corresponding to :ref:`ISIS_NEIGHBOR_DOWN` is 
named ``napalm_logs_isis_neighbor_down``.

All the metrics have at least the ``host`` label. Some of them have additional
labels, whenever it makes sense to include additional information that can be 
used for selection and/or alerting.

By default, it will expose metrics for all kinds of messages, so you might want
to narrow down the selection using the :ref:`publisher-opts-error-whitelist` or
:ref:`publisher-opts-error-blacklist` options.

CLI usage example:

.. code-block:: bash

  $ sudo napalm-logs --publisher prometheus --enable-metrics

Starting through the command above, you'll find the metrics at 
http://localhost:9443/metrics.

Metrics examples:

.. code-block:: text

  # HELP napalm_logs_interface_up_total Multiprocess metric
  # TYPE napalm_logs_interface_up_total counter
  napalm_logs_interface_up_total{host="veos01",interface="Ethernet28"} 1.0
  # HELP napalm_logs_interface_down_total Multiprocess metric
  # TYPE napalm_logs_interface_down_total counter
  napalm_logs_interface_down_total{host="veos01",interface="Ethernet28"} 1.0
  # HELP napalm_logs_isis_neighbor_down_total Multiprocess metric
  # TYPE napalm_logs_isis_neighbor_down_total counter
  napalm_logs_isis_neighbor_down_total{host="HOSTNAME",interface="et7",level="L1",neighbor="1920.0000.2006"} 1.0
  # HELP napalm_logs_bgp_neighbor_state_changed_total Multiprocess metric
  # TYPE napalm_logs_bgp_neighbor_state_changed_total counter
  napalm_logs_bgp_neighbor_state_changed_total{current_state="IDLE",host="HOSTNAME",neighbor="192.0.2.2",peer_as="12345",previous_state="ESTABLISHED"} 1.0
  # HELP napalm_logs_agent_initialized_total Multiprocess metric
  # TYPE napalm_logs_agent_initialized_total counter
  napalm_logs_agent_initialized_total{host="edge01.bru01"} 1.0
  # HELP napalm_logs_interface_mac_limit_reached Multiprocess metric
  # TYPE napalm_logs_interface_mac_limit_reached gauge
  napalm_logs_interface_mac_limit_reached{host="vmx01",interface="ge-1/0/23.0",pid="15711"} 3.0
