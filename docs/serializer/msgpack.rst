.. _serializer-msgpack:

===========
MessagePack
===========

This is the default Serializer used by napalm-logs.

  MessagePack is an efficient binary serialization format. It lets you exchange
  data among multiple languages like JSON. But it's faster and smaller. Small
  integers are encoded into a single byte, and typical short strings require
  only one extra byte in addition to the strings themselves.

Source: `MessagePack <https://msgpack.org/>`_.

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

The document will be binary serialized as:

.. code-block:: none

  \x8a\xacyang_message\x81\xa3bgp\x81\xa9neighbors\x81\xa8neighbor\x81\xaf192.168.140.254\x81\xa5state\x81\xadsession_state\xa7CONNECT\xafmessage_details\x8b\xa9processId\xc0\xa8severity\x04\xa8facility\x00\xaahostPrefix\xc0\xa3pri\xa14\xabprocessName\xa6kernel\xa4host\xa5vmx01\xa3tag\xabtcp_auth_ok\xa4time\xa821:23:00\xa4date\xa6Jul 20\xa7message\xd92Packet from 192.168.140.254:61664 wrong MD5 digest\xa8facility\x00\xa2ip\xa9127.0.0.1\xa5error\xb1BGP_MD5_INCORRECT\xa4host\xa5vmx01\xaayang_model\xaeopenconfig-bgp\xa9timestamp\xceYq\x1f4\xa2os\xa5junos\xa8severity\x04


