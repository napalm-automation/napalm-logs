===========
Napalm-logs
===========

Python library to parse syslog messages from network devices and produce JSON serializable Python objects, in a vendor agnostic shape. The output objects are structured following the OpenConfig or IETF YANG models.

For example, the following syslog message from a Juniper device:

.. code-block:: text

    Mar 30 12:45:19 re0.edge01.bjm01 rpd[15852]: BGP_PREFIX_THRESH_EXCEEDED 1.2.3.4 (External AS 15169): Configured maximum prefix-limit threshold(160) exceeded for inet-unicast nlri: 181 (instance master)


Will produce the following object:

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
  }


Thie library is provided with a command line program which acts as a daemon, running in background and listening to syslog messages continuously, then publishing them over secured channels, where multiple clients can subscribe.

It is flexible to listen to the syslog messages via UDP or TCP, but also from brokers such as Apache Kafka. Similarly, the output objects can be published via various channels such as ZeroMQ, Kafka, or remote server logging. It is also pluggable enough to extend these capabilities and listen or publish to other services, depending on the needs.

The messages are published over a secured channel, encrypted and signed. Although the security can be disabled, this is highly discouraged.

Install
-------
napalm-logs is available on PyPi and can easily be installed using the following command:

.. code-block:: bash

    pip install napalm-logs
