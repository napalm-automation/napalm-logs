==========================
BGP_PREFIX_THRESH_EXCEEDED
==========================

This error tag corresponds to syslog messages notifying that the prefix limit threshhold for a BGP neighbor has been exceeded and the neighbor has been torn down.

Maps to the ``openconfig_bgp`` YANG model.

Implemented for:

- junos
- iosxr
- eos

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
					"inet": {
					  "state": {
						"prefixes": {
						  "received": "28"
						}
					  },
					  "ipv4_unicast": {
						"prefix_limit": {
						  "state": {
							"max_prefixes": "3"
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
		"processId": "2965",
		"hostPrefix": null,
		"pri": "28",
		"processName": "rpd",
		"host": "vmx01",
		"tag": "BGP_PREFIX_LIMIT_EXCEEDED",
		"time": "18:45:25",
		"date": "Jul 20",
		"message": "192.168.140.254 (External AS 65001): Configured maximum prefix-limit(3) exceeded for inet-unicast nlri: 28 (instance master)"
	  },
	  "timestamp": 1500572725,
	  "facility": 3,
	  "ip": "192.168.140.252",
	  "host": "vmx01",
	  "yang_model": "openconfig_bgp",
	  "error": "BGP_PREFIX_LIMIT_EXCEEDED",
	  "os": "junos",
	  "severity": 4
	}

