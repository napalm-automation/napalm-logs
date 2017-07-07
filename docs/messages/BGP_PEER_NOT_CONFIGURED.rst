=======================
BGP_PEER_NOT_CONFIGURED
=======================

This error tag corresponds to syslog messages notifying that the configured peer sent a BGP notification code 6 subcode 5, which idicates that the peer does not have the session configured.

Maps to the ``openconfig_bgp`` YANG model.

Implemented for:

- junos

Example:

.. code-block:: json

	{
	  "message_details": {
		"processId": "1848",
		"hostPrefix": null,
		"pri": "28",
		"processName": "rpd",
		"host": "vmx01",
		"tag": "bgp_read_message",
		"time": "05:52:44",
		"date": "Jul  5",
		"message": "2764: NOTIFICATION received from 1.2.3.4 (External AS 1234): code 6 (Cease) subcode 5 (Connection Rejected)"
	  },
	  "open_config": {
		"bgp": {
		  "neighbors": {
			"neighbor": {
			  "1.2.3.4": {
				"state": {
				  "session_state": "ACTIVE",
				  "peer_as": 1234
				},
				"neighbor_address": "1.2.3.4"
			  }
			}
		  }
		}
	  },
	  "ip": "127.0.0.1",
	  "error": "BGP_PEER_NOT_CONFIGURED",
	  "host": "vmx01",
	  "timestamp": "1499230364",
	  "os": "junos",
	  "model_name": "openconfig_bgp"
	}

