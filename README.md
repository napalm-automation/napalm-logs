# napalm-logs

napalm-logs is a Python library that listens to syslog messages from network
devices and returns strucuted data following the [OpenConfig](http://www.openconfig.net/)
or [IETF](https://github.com/YangModels/yang/tree/master/standard/ietf) YANG models.

<img src="logo.png" data-canonical-src="logo.png" width="300" />

The outgoing objects are published via ZeroMQ, Kafka, or other usual transport
options. It is easy enough to switch between transports and pluggable to add
others such as Google Datastore, RabbitMQ, etc.

Similarly, the syslog messages can be received via UDP, TCP, or different
services, such as  Kafka, etc.

New platforms can be easily added, just referencing the path to the
YAML configuration file.

Requirements
------------

- PyYAML
- PyZMQ
- PyNaCl
- u-msgpack-python

Output object example
---------------------

```json
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
                      "received": 141
                    }
                  },
                  "ipv4_unicast": {
                    "prefix_limit": {
                      "state": {
                        "max_prefixes": 140
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
    "facility": 18,
    "severity": 5
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
  "yang_model": "openconfig-bgp",
  "error": "BGP_PREFIX_THRESH_EXCEEDED",
  "os": "junos",
  "severity": 5
}
```

Documentation
-------------

Please check [the official documentation](http://napalm-logs.readthedocs.io/en/latest/) for more detailed information.

Installation
------------

```
pip install napalm-logs
```
