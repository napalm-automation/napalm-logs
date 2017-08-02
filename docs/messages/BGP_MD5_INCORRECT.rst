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
	  "yang_message": {
		"bgp": {
		  "neighbors": {
			"neighbor": {
			  "192.168.140.254": {
				"state": {
				  "session_state": "CONNECT"
				}
			  }
			}
		  }
		}
	  },
	  "message_details": {
		"processId": null,
		"hostPrefix": null,
		"pri": "4",
		"processName": "kernel",
		"host": "vmx01",
		"tag": "tcp_auth_ok",
		"time": "18:19:48",
		"date": "Jul 20",
		"message": "Packet from 192.168.140.254:53921 wrong MD5 digest"
	  },
	  "timestamp": 1500571188,
	  "facility": 0,
	  "ip": "192.168.140.252",
	  "host": "vmx01",
	  "yang_model": "openconfig_bgp",
	  "error": "BGP_MD5_INCORRECT",
	  "os": "junos",
	  "severity": 4
	}

