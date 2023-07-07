.. _syslog:

=================================
The format of the syslog messages
=================================

While the structure of the syslog messages should not be very much different
than the base `IEFT syslog protocol <https://tools.ietf.org/html/rfc5424>`_,
each platform has its own format which does not necessarily commit to the
standards.

As in opposite to the `standard structure <https://www.balabit.com/documents/syslog-ng-ose-latest-guides/en/syslog-ng-ose-guide-admin/html/concepts-message-ietfsyslog.html>`_, the most
common format of the syslog messages has two components:

- :ref:`syslog-header` (including :ref:`syslog-pri`)
- :ref:`syslog-msg`

In general their format varies between platforms, the structure being explained
in the following documents, individually:

.. toctree::
   :maxdepth: 1

   junos
   iosxr
   eos
   nxos

.. _syslog-pri:

PRI
---

The Priority value is calculated by first multiplying the Facility number by 8
and then adding the numerical value of the Severity. For example, a kernel
message (Facility=0) with a Severity of Emergency (Severity=0) would have a
Priority value of 0.

In addition to the `standard PRI <https://www.balabit.com/documents/syslog-ng-ose-latest-guides/en/syslog-ng-ose-guide-admin/html/ietfsyslog-pri.html>`_ classification, each platform defines additional
values for Facility which may differ from a platform to another.

The Severity however usually respects the standard:

+----------------+------------------+------------------------------------------+
| Numerical code | Severity level   | Description                              |
+================+==================+==========================================+
| 0              | emergency        | System panic or other condition that     |
|                |                  | causes the router to stop functioning    |
+----------------+------------------+------------------------------------------+
| 1              | alert            | Conditions that require immediate        |
|                |                  | correction, such as a corrupted          |
|                |                  | system database                          |
+----------------+------------------+------------------------------------------+
| 2              | critical         | Critical conditions, such as hard errors |
+----------------+------------------+------------------------------------------+
| 3              | error            | Error conditions that generally have less|
|                |                  | serious consequences than errors in the  |
|                |                  | emergency, alert, and critical levels    |
+----------------+------------------+------------------------------------------+
| 4              | warning          | Conditions that warrant monitoring       |
+----------------+------------------+------------------------------------------+
| 5              | notice           | Conditions that are not errors but       |
|                |                  | might warrant special handling           |
+----------------+------------------+------------------------------------------+
| 6              | info             | Events or nonerror conditions of interest|
+----------------+------------------+------------------------------------------+
| 7              | debug            | Software debugging messages (these appear|
|                |                  | only if a technical support              |
|                |                  | representative has instructed you to     |
|                |                  | configute this severity level            |
+----------------+------------------+------------------------------------------+

.. _syslog-header:

HEADER
------

The syslog messages from network devices do not respect the `standard HEADER <https://www.balabit.com/documents/syslog-ng-ose-latest-guides/en/syslog-ng-ose-guide-admin/html/ietfsyslog-header.html>`_.

.. _syslog-msg:

MSG
---

The MSG part contains the text of the message itself.

Date and Time Notes
-------------------

Most syslog messages do not incude the year in the message timestamp. Napalm-logs overcomes this by appending the year from the server. While rare, it is possible to form an invalid date when the device
emitting the syslog has an incorrect local time set (e.g. February 29, 2018 where 2018 is not a leap year). In such cases, Napalm-logs falls back to using the date and time of the server.
