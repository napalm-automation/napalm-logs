=================
BGP_MD5_INCORRECT
=================

This error tag corresponds to syslog messages notifying that the authentication for a BGP neighbor is incorrect.

Maps to the ``openconfig_bgp`` YANG model.

Implemented for:

- junos

Example:

.. code-block:: json

    {
      "message_details": {
        "processId": null,
        "hostPrefix": null,
        "pri": "4",
        "processName": "kernel",
        "host": "vmx01",
        "tag": "tcp_auth_ok",
        "time": "07:51:06",
        "date": "Jun  9",
        "message": "Packet from 192.168.140.254:56721 wrong MD5 digest"
      },
      "open_config": {
        "bgp": {
          "neighbors": {
            "neighbor": {
              "192.168.140.254": {
                "state": {
                  "session_state": "CONNECT"
                },
                "neighbor_address": "192.168.140.254"
              }
            }
          }
        }
      },
      "ip": "192.168.140.252",
      "error": "BGP_MD5_INCORRECT",
      "host": "vmx01",
      "timestamp": "1496991066",
      "os": "junos",
      "model_name": "openconfig_bgp"
    }

