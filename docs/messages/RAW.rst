===
RAW
===

This error tag is sent when napalm-logs was able to identify the operating
system, but there was no tag matching the syslog message. Therefore, the
output object will contain the syslog message parts, without further processing.
By default, these messages are not published; they need to be explicitly
enabled using the :ref:`publisher-opts-send-raw` option for the publisher.

.. note::

  These messages are not recommended for production use.
  They can be used as temporary helpers, at most.
  The right approach is appending a new message matcher inside the
  corresponding device profile. See :ref:`device-profiles`.

.. note::

  The syslog message parts under the ``message_details`` key are device-specific,
  as designed inside the profiler.

Example:

.. code-block:: json

  {
    "message_details": {
      "processId": null,
      "hostPrefix": null,
      "pri": "37",
      "processName": "sshd",
      "host": "vmx1",
      "tag": "SSHD_LOGIN_FAILED",
      "time": "10:32:03",
      "date": "Jul 10",
      "message": "Login failed for user 'root' from host '61.177.172.56'"
    },
    "ip": "172.17.17.1",
    "host": "vmx1",
    "timestamp": "1499682723",
    "os": "junos",
    "model_name": "raw",
    "error": "RAW"
  }
