.. _serializer-str:

======
String
======

Simply a string representation of the Python object. This Serializer can mainly 
be used for CLI debugging.

For example, given the following napalm-logs document (as JSON):

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

The document will be serialized as:

.. code-block:: none

	{u'yang_message': {u'bgp': {u'neighbors': {u'neighbor': {u'192.168.140.254': {u'state': {u'session_state': u'CONNECT'}}}}}}, u'message_details': {u'processId': None, u'severity': 4, u'facility': 0, u'hostPrefix': None, u'pri': u'4', u'processName': u'kernel', u'host': u'vmx01', u'tag': u'tcp_auth_ok', u'time': u'21:23:00', u'date': u'Jul 20', u'message': u'Packet from 192.168.140.254:61664 wrong MD5 digest'}, u'facility': 0, u'ip': u'127.0.0.1', u'error': u'BGP_MD5_INCORRECT', u'host': u'vmx01', u'yang_model': u'openconfig-bgp', u'timestamp': 1500585780, u'os': u'junos', u'severity': 4}
