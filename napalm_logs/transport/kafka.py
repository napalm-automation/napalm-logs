# -*- coding: utf-8 -*-
"""
Kafka transport for napalm-logs.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

# Import stdlib
import logging

# Import third party libs
try:
    import kafka

    HAS_KAFKA = True
except ImportError:
    HAS_KAFKA = False

# Import napalm-logs pkgs
from napalm_logs.exceptions import NapalmLogsException
from napalm_logs.transport.base import TransportBase

log = logging.getLogger(__name__)
kafka_producer_opts = {
    "batch_size": 16384,
    "max_request_size": 1048576,
    "buffer_memory": 33554432, #32MB
    "send_buffer_bytes": 131072,
    "max_in_flight_requests_per_connection": 5,
    "retries": 0,
    "max_block_ms": 60000,
    "linger_ms": 0
}

class KafkaTransport(TransportBase):
    """
    Kafka transport class.
    """

    def __init__(self, address, port, **kwargs):
        if kwargs.get("address"):
            address = kwargs["address"]
        if kwargs.get("port"):
            address = kwargs["port"]
        if kwargs.get("no_encrypt"):
            self.NO_ENCRYPT = kwargs["no_encrypt"]
        if kwargs.get("bootstrap_servers"):
            self.bootstrap_servers = kwargs["bootstrap_servers"]
        else:
            self.bootstrap_servers = "{}:{}".format(address, port)
        if kwargs.get("opts"):
            self.opts = kwargs["opts"]
        else:
            self.opts = kafka_producer_opts
        self.kafka_topic = kwargs.get("topic", "napalm-logs")

    def start(self):
        try:
            self.producer = kafka.KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                batch_size=self.opts.get("batch_size", kafka_producer_opts["batch_size"]),
                max_request_size=self.opts.get("max_request_size", kafka_producer_opts["max_request_size"]),
                buffer_memory=self.opts.get("buffer_memory", kafka_producer_opts["buffer_memory"]),
                send_buffer_bytes=self.opts.get("send_buffer_bytes", kafka_producer_opts["send_buffer_bytes"]),
                max_in_flight_requests_per_connection=self.opts.get("max_in_flight_requests_per_connection", kafka_producer_opts["max_in_flight_requests_per_connection"]),
                retries=self.opts.get("retries", kafka_producer_opts["retries"]),
                max_block_ms=self.opts.get("max_block_ms", kafka_producer_opts["max_block_ms"]),
                linger_ms=self.opts.get("linger_ms", kafka_producer_opts["linger_ms"]),
             )
        except kafka.errors.NoBrokersAvailable as err:
            log.error(err, exc_info=True)
            raise NapalmLogsException(err)

    def publish(self, obj):
        if isinstance(obj, str):
            obj = obj.encode()
        self.producer.send(self.kafka_topic, obj)

    def stop(self):
        if hasattr(self, "producer"):
            self.producer.close()
