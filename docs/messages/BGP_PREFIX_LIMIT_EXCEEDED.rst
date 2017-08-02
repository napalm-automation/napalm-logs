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
	  "yang_message": {
		"bgp": {
		  "neighbors": {
			"neighbor": {
			  "192.168.140.254": {
				"state": {
				  "peer_as": "65001"
				},
				"afi_safis": {
				  "afi_safi": {
					"inet4": {
					  "state": {
						"prefixes": {
						  "received": "141"
						}
					  },
					  "ipv4_unicast": {
						"prefix_limit": {
						  "state": {
							"max_prefixes": "140"
						  }
						}
					  }
					}
				  }
				}
			  }
			}
		  }
		}
	  },
	  "message_details": {
		"processId": "2902",
		"hostPrefix": null,
		"pri": "149",
		"processName": "rpd",
		"host": "vmx01",
		"tag": "BGP_PREFIX_THRESH_EXCEEDED",
		"time": "14:03:12",
		"date": "Jun 21",
		"message": "192.168.140.254 (External AS 65001): Configured maximum prefix-limit threshold(140) exceeded for inet4-unicast nlri: 141 (instance master)"
	  },
	  "timestamp": 1498050192,
	  "facility": 18,
	  "ip": "127.0.0.1",
	  "host": "vmx01",
	  "yang_model": "openconfig_bgp",
	  "error": "BGP_PREFIX_THRESH_EXCEEDED",
	  "os": "junos",
	  "severity": 5
	}

