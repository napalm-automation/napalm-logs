# -*- coding: utf-8 -*-
'''
Kafka transport for napalm-logs.
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import stdlib
import json
import logging

# Import third party libs
try:
    import kafka
    HAS_KAFKA = True
except ImportError as err:
    HAS_KAFKA = False

# Import napalm-logs pkgs
from napalm_logs.exceptions import NapalmLogsException
from napalm_logs.transport.base import TransportBase
from napalm_logs.config import KAFKA_PUBLISHER_TOPIC

log = logging.getLogger(__name__)


class KafkaTransport(TransportBase):
    '''
    Kafka transport class.
    '''
    def __init__(self, addr, port):
        self.bootstrap_servers = '{addr}:{port}'.format(addr=addr, port=port)
        self.topic = KAFKA_PUBLISHER_TOPIC

    def start(self):
        try:
            self.producer = kafka.KafkaProducer(bootstrap_servers=self.bootstrap_servers)
        except kafka.errors.NoBrokersAvailable as err:
            log.error(err, exc_info=True)
            raise NapalmLogsException(err)

    def publish(self, obj):
        self.producer.send(self.topic, obj)

    def stop(self):
        if hasattr(self, 'producer'):
            self.producer.close()
