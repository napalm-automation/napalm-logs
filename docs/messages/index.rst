===================
Structured Messages
===================

Each message has a certain identification tag which is unique and cross-platform.

For example, the following syslog message:

.. code-block:: text

	<28>Jul  4 13:40:55 vmx2 rpd[2942]: BGP_PREFIX_LIMIT_EXCEEDED: 10.0.0.31 (Internal AS 65001): Configured maximum prefix-limit(1) exceeded for inet-unicast nlri: 7 (instance master)

``napalm-logs`` identifies that it was produced by a Junos device and assigns the error tag ``BGP_PREFIX_LIMIT_EXCEEDED`` and then will try to map the information into the OpenConfig model ``openconfig_bgp``:

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
      "timestamp": "1499175325",
      "os": "junos",
      "model_name": "openconfig_bgp"
    }

Under this section, we present the possible error tags, together with their corresponding YANG model and examples.

.. toctree::
   :maxdepth: 1

   BGP_MD5_INCORRECT
   BGP_PREFIX_THRESH_EXCEEDED
   BGP_PREFIX_LIMIT_EXCEEDED
