.. _device-configuration-sonic:

===========
Azure SONiC
===========

.. versionadded:: 0.8.0

The following will configure Azure Sonic to send syslog messages, over UDP, to the 
IP Address ``10.10.10.1``, port 514 and using the syslog-protocol-23 format.

The Rsyslogd is configured via the rsyslog.conf file, found in ``/etc``.


First, configure Rsyslogd to use the SyslogProtocol23Format template

.. code-block:: text

    $template RSYSLOG_SyslogProtocol23Format,"<%PRI%>1 %TIMESTAMP:::date-rfc3339% %HOSTNAME% %APP-NAME% %PROCID% %MSGID% %STRUCTURED-DATA%%msg%\n"

Then, set the remote syslog server

.. code-block:: text

    *.* @10.10.10.1:514;RSYSLOG_SyslogProtocol23Format

To correctly send the hostname information, it is also recommended to explicitly
configure the following:

.. code-block:: text

    $PreserveFQDN on
