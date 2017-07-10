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
    "ip": "172.17.17.1",
    "host": "edge01.bjm01",
    "message_details": {
      "processId": "15852",
      "error": "BGP_PREFIX_THRESH_EXCEEDED",
      "pri": "149",
      "processName": "rpd",
      "host": "edge01.bjm01",
      "time": "12:45:19",
      "date": "Mar 30",
      "message": "1.2.3.4 (External AS 15169): Configured maximum prefix-limit threshold(160) exceeded for inet-unicast nlri: 181 (instance master)"
    },
    "open_config": {
      "bgp": {
        "neighbors": {
          "neighbor": {
            "1.2.3.4": {
              "neighbor-address": "1.2.3.4",
              "state": {
                "peer-as": 15169
              },
              "afi-safis": {
                "afi-safi": {
                  "inet": {
                    "state": {
                      "prefixes": {
                        "received": 181
                      }
                    },
                    "ipv4-unicast": {
                      "prefix-limit": {
                        "state": {
                          "max-prefixes": 160
                        }
                      }
                    },
                    "afi-safi-name": "inet"
                  }
                }
              }
            }
          }
        }
      }
    },
    "timestamp": "1490877919"
  }


Thie library is provided with a command line program which acts as a daemon, running in background and listening to syslog messages continuously, then publishing them over secured channels, where multiple clients can subscribe.

It is flexible to listen to the syslog messages via UDP or TCP, but also from brokers such as Apache Kafka. Similarly, the output objects can be published via various channels such as ZeroMQ, Kafka, or remote server logging. It is also pluggable enough to extend these capabilities and listen or publish to other services, depending on the needs.

The messages are published over a secured channel, encrypted and signed. Although the security can be disabled, this is highly discouraged.

Install
-------
napalm-logs is available on PyPi and can easily be installed using the following command:

.. code-block:: bash

    pip install napalm-logs
