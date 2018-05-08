.. _metrics:

==================
Metrics Collection
==================

Timeseries metrics my be optionally collected and exported from the server.
This feature is dissabled by default but can be enabled by passing `--enable-metrics`
when envoking the server.

The metrics offer insight into how the server is processing messages. Each subsystem publishes
its own set of metrics. These are timeserises data so they are mostly counters of processed
elements.

We use the Prometheus metrics format and the metrics are exposed by an HTTP server which by default
run on for 9215. The implementation is fully complient with Prometheus scraping, so you need only
point your Prometheus server to the exposed metrics to scrape them.
