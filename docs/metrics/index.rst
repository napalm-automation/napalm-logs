.. _metrics:

==================
Metrics Collection
==================

Timeseries metrics may be optionally collected and exported from the server.
This feature is disabled by default but can be enabled by passing `--enable-metrics`
when envoking the server.

The metrics offer insight into how the server is processing messages. Each subsystem publishes
its own set of metrics. These are timeseries data so they are mostly counters of processed
elements.

We use the Prometheus metrics format and the metrics are exposed by an HTTP server which by default
run on port tcp/9443. The implementation is fully compliant with Prometheus scraping, so you need only
point your Prometheus server to the exposed metrics to scrape them.

When using the feature, you must make a directory available which will be used to collect and store
local metrics from the various system processes. The server will need rights to write to this
directory. By default `/tmp/napalm_logs_metrics` is used. This is configurable with
`--metrics-dir`. Whatever the value, if the directory does not exist, we attempt to create it
on startup. Also note than this directory is cleared of all previous metrics entries on each run.
This means that metric values are not persisted through runs.

Here is a listing of the exposed metrics and their meaning:

Listener Process(es)
--------------------

napalm_logs_listener_logs_ingested
  Count of ingested log messages. Labels are used to seperate metrics for each Listener process.

napalm_logs_listener_messages_published
  Count of published messages. These are messages published to the message queue for processing by the Server Process.
  Labels are used to seperate metrics for each Listener process.

Server Process
--------------

napalm_logs_server_messages_received
  Count of messages received from Listener processes.

napalm_logs_server_messages_with_identified_os
  Count of messages with positive OS identification. Labels are used to seperate metrics for each Device OS.

napalm_logs_server_messages_without_identified_os
  Count of messages which fail OS identification.

napalm_logs_server_messages_failed_device_queuing
  Count of messages per device OS that fail to be queued to a proper Device process. Note these are messages that
  pass OS identification and we know how to route them but fail to be queued. Labels are used to seperate metrics
  for each Device OS.

napalm_logs_server_messages_device_queued
  Count of messages sucessfully queued to Device processes. Labels are used to seperate metrics for each Device OS process.

napalm_logs_server_messages_unknown_queued
  Count of messages which fail OS indentification and thus we don't know how to route them, but the user has instructed
  the system to queue them "as-is."

Device Process(es)
------------------

napalm_logs_device_messages_received
  Count of messages received from the Server process. Labels are used to seperate metrics for each Device OS process.

napalm_logs_device_raw_published_messages
  Count of raw type published messages. In this case, the message did not match a configured message type but the
  user has instructed the system to publish the message in a raw format. Labels are used to seperate metrics for
  each Device OS process.

napalm_logs_device_published_messages
  Count of published messages. These are messages which are sucessfully converted to an OpenConfig format. Labels
  are used to seperate metrics for each Device OS process.

napalm_logs_device_oc_object_failed 
  Counter of failed OpenConfig object generations. These are messages for which the system attempts to map to a
  known OpenConfig object model but fails. Labels are used to seperate metrics for each Device OS process.

Publisher Process(es)
---------------------

napalm_logs_publisher_received_messages
  Count of messages received by the Publisher from Device Process(es). Labels are used to seperate metrics for
  each Publisher process.

napalm_logs_publisher_whitelist_blacklist_check_fail
  Count of messages which fail the whitelist/blacklist check. Labels are used to seperate metrics for each
  Publisher process.

napalm_logs_publisher_messages_published
  Count of published messages. These are messages which are published for clients to receive (i.e. output of the
  system). Labels are used to seperate metrics for each Publisher process.
