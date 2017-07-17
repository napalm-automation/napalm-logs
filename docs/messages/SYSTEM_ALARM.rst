============
SYSTEM_ALARM
============

This error tag corresponds to syslog messages notifying that there has been a change in status for an alarm.

There are multiple entries for this error. The reason being that the exact component name can be contained in the reason section, so has to be extracted via a specific regex.

Maps to the ``ietf-hardware`` YANG model.

Implemented for:

- junos

Example:

.. code-block:: json

	{
	  "yang_message": {
		"hardware-state": {
		  "component": {
			"FPC 0": {
			  "state": {
				"alarm-reason": "FPC 0 Major Errors",
				"alarm-state": 3
			  },
			  "name": "FPC 0",
			  "class": "CHASSIS"
			}
		  }
		}
	  },
	  "message_details": {
		"processId": "2449",
		"hostPrefix": null,
		"pri": "29",
		"processName": "alarmd",
		"host": "vmx01",
		"tag": "Alarm set",
		"time": "23:04:13",
		"date": "Jul  8",
		"message": "FPC color=RED, class=CHASSIS, reason=FPC 0 Major Errors"
	  },
	  "timestamp": "1499551453",
	  "ip": "127.0.0.1",
	  "host": "vmx01",
	  "yang_model": "ietf-hardware",
	  "error": "SYSTEM_ALARM",
	  "os": "junos"
	}

