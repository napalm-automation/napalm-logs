=========================
BGP_PREFIX_LIMIT_EXCEEDED
=========================

This error tag corresponds to syslog messages notifying that the prefix limit for a BGP neighbor has been exceeded, without tearing it down.

Maps to the ``openconfig_bgp`` YANG model.

Implemented for:

- junos

Example:

.. code-block:: json

    {
      "message_details": {
        "processId": "2942",
        "hostPrefix": null,
        "pri": "28",
        "processName": "rpd",
        "host": "vmx2",
        "tag": "BGP_PREFIX_LIMIT_EXCEEDED",
        "time": "13:35:25",
        "date": "Jul  4",
        "message": "10.0.0.31 (Internal AS 65001): Configured maximum prefix-limit(1) exceeded for inet-unicast nlri: 7 (instance master)"
      },
      "open_config": {
        "bgp": {
          "neighbors": {
            "neighbor": {
              "10.0.0.31": {
                "state": {
                  "peer_as": 65001
                },
                "afi_safis": {
                  "afi_safi": {
                    "inet": {
                      "state": {
                        "prefixes": {
                          "received": 7
                        }
                      },
                      "afi_safi_name": "inet",
                      "ipv4_unicast": {
                        "prefix_limit": {
                          "state": {
                            "max_prefixes": 1
                          }
                        }
                      }
                    }
                  }
                },
                "neighbor_address": "10.0.0.31"
              }
            }
          }
        }
      },
      "ip": "130.211.119.212",
      "error": "BGP_PREFIX_LIMIT_EXCEEDED",
      "host": "vmx2",
      "timestamp": 1499175325,
      "os": "junos",
      "model_name": "openconfig_bgp"
    }

