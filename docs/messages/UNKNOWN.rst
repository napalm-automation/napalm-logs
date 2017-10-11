.. _UNKNOWN:

=======
UNKNOWN
=======

This error tag is sent when napalm-logs was unable to identify the operating
system. By default, these messages are not published; they need to be explicitly
enabled using the :ref:`publisher-opts-send-unknown` option for the publisher.

.. note::

  These messages are not recommended for production use.
  They can be used as temporary helpers, at most.
  The right approach is writing a new device profile matching the syslog message
  and generating the structured messages as required. See :ref:`device-profiles`.

Example:

.. code-block:: json

	{
	  "message_details": {
		"message": "<28>Jul 10 10:32:00 vmx1 inetd[2397]: /usr/sbin/sshd[89736]: exited, status 255\n"
	  },
	  "timestamp": 1501685287,
	  "ip": "127.0.0.1",
	  "host": "unknown",
	  "error": "UNKNOWN",
	  "os": "unknown",
	  "model_name": "unknown"
	}

