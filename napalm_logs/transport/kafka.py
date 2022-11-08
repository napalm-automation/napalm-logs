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
        self.kafka_topic = kwargs.get("topic", "napalm-logs")

    def start(self):
        try:
            self.producer = kafka.KafkaProducer(
                bootstrap_servers=self.bootstrap_servers
            )
        except kafka.errors.NoBrokersAvailable as err:
            log.error(err, exc_info=True)
            raise NapalmLogsException(err)

    def publish(self, obj):
        self.producer.send(self.kafka_topic, obj)

    def stop(self):
        if hasattr(self, "producer"):
            self.producer.close()
