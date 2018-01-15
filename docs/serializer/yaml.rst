.. _serializer-yaml:

====
YAML
====

The structured messages can be YAML serialized. This can be used for a variety 
of cases, including CLI usage for a human readable display, but also for other
Publisher interfaces.

Given the following napalm-logs document (as JSON):

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
		"severity": 4,
		"facility": 0,
		"hostPrefix": null,
		"pri": "4",
		"processName": "kernel",
		"host": "vmx01",
		"tag": "tcp_auth_ok",
		"time": "21:23:00",
		"date": "Jul 20",
		"message": "Packet from 192.168.140.254:61664 wrong MD5 digest"
	  },
	  "timestamp": 1500585780,
	  "facility": 0,
	  "ip": "127.0.0.1",
	  "host": "vmx01",
	  "yang_model": "openconfig-bgp",
	  "error": "BGP_MD5_INCORRECT",
	  "os": "junos",
	  "severity": 4
	}

The document will be YAML serialized as:

.. code-block:: yaml

	error: BGP_MD5_INCORRECT
	facility: 0
	host: vmx01
	ip: 127.0.0.1
	message_details:
	  date: Jul 20
	  facility: 0
	  host: vmx01
	  hostPrefix: null
	  message: Packet from 192.168.140.254:61664
		wrong MD5 digest
	  pri: 4
	  processId: null
	  processName: kernel
	  severity: 4
	  tag: tcp_auth_ok
	  time: 21:23:00
	os: junos
	severity: 4
	timestamp: 1500585780
	yang_message:
	  bgp:
		neighbors:
		  neighbor:
			192.168.140.254:
			  state:
				session_state: CONNECT
	yang_model: openconfig-bgp
