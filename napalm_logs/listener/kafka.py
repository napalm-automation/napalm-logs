# -*- coding: utf-8 -*-
"""
Kafka listener for napalm-logs.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

# Import stdlib
import json
import time
import logging

# Import third party libs
try:
    import kafka

    HAS_KAFKA = True
except ImportError:
    HAS_KAFKA = False

# Import napalm-logs pkgs
from napalm_logs.listener.base import ListenerBase
from napalm_logs.exceptions import ListenerException

log = logging.getLogger(__name__)


class KafkaListener(ListenerBase):
    """
    Kafka listener class.
    """

    def __init__(self, address, port, **kwargs):
        if kwargs.get("address"):
            address = kwargs["address"]
        if kwargs.get("port"):
            port = kwargs["port"]
        self.bootstrap_servers = kwargs.get(
            "bootstrap_servers", "{}:{}".format(address, port)
        )
        self.group_id = kwargs.get("group_id", "napalm-logs")
        self.topic = kwargs.get("topic", "syslog.net")

    def start(self):
        """
        Startup the kafka consumer.
        """
        log.debug(
            "Creating the consumer using the bootstrap servers: %s and the group ID: %s",
            self.bootstrap_servers,
            self.group_id,
        )
        try:
            self.consumer = kafka.KafkaConsumer(
                bootstrap_servers=self.bootstrap_servers, group_id=self.group_id
            )
        except kafka.errors.NoBrokersAvailable as err:
            log.error(err, exc_info=True)
            raise ListenerException(err)
        log.debug("Subscribing to the %s topic", self.topic)
        self.consumer.subscribe(topics=[self.topic])

    def receive(self):
        """
        Return the message received and the address.
        """
        try:
            msg = next(self.consumer)
        except ValueError as error:
            log.error("Received kafka error: %s", error, exc_info=True)
            raise ListenerException(error)
        log_source = msg.key
        try:
            decoded = json.loads(msg.value.decode("utf-8"))
        except ValueError:
            log.error("Not in json format: %s", msg.value.decode("utf-8"))
            return "", ""
        log_message = decoded.get("message")
        log.debug("[%s] Received %s from %s", log_message, log_source, time.time())
        return log_message, log_source

    def stop(self):
        """
        Shutdown kafka consumer.
        """
        log.info("Stopping te kafka listener class")
        self.consumer.unsubscribe()
        self.consumer.close()
