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

In addition to the `standard PRI <https://www.balabit.com/documents/syslog-ng-ose-latest-guides/en/syslog-ng-ose-guide-admin/html/ietfsyslog-pri.html>`_ classification, each platform defines additional
values for Facility and Severity which may differ from a platform to another.

.. _syslog-header:

HEADER
------

The syslog messages from network devices do not respect the `standard HEADER <https://www.balabit.com/documents/syslog-ng-ose-latest-guides/en/syslog-ng-ose-guide-admin/html/ietfsyslog-header.html>`_.

.. syslog-msg:

MSG
---

The MSG part contains the text of the message itself.
