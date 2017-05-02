# -*- coding: utf-8 -*-
'''
napalm-logs pluggable publisher.
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import napalm-logs pkgs
from napalm_logs.transport.base import TransportBase
from napalm_logs.transport.zeromq import ZMQTransport
from napalm_logs.transport.kafka import KafkaTransport
from napalm_logs.transport.kafka import HAS_KAFKA
from napalm_logs.transport.cli import CLITransport
from napalm_logs.transport.log import LogTransport
# from napalm_logs.transport.kafka import KafkaTransport
# from napalm_logs.transport.rabbitmq import RabbitMQTransport

TRANSPORT_LOOKUP = {
    'zeromq': ZMQTransport,
    'zmq': ZMQTransport,
    'cli': CLITransport,
    'print': CLITransport,
    'console': CLITransport,
    'log': LogTransport,
    # 'rmq': RabbitMQransport,
    # 'rabbitmq': RabbitMQransport,
    '*': ZMQTransport  # default transport
}

if HAS_KAFKA:
    TRANSPORT_LOOKUP['kafka'] = KafkaTransport

def get_transport(name):
    '''
    Return the transport class.
    '''
    return TRANSPORT_LOOKUP.get(name, TRANSPORT_LOOKUP['*'])

__all__ = (
    'get_transport',
)
