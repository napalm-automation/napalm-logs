# -*- coding: utf-8 -*-
'''
napalm-logs pluggable listener.
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import napalm-logs pkgs
from napalm_logs.listener.base import ListenerBase
from napalm_logs.listener.kafka import KafkaListener
from napalm_logs.listener.tcp import TCPListener
from napalm_logs.listener.udp import UDPListener
from napalm_logs.listener.kafka import HAS_KAFKA

LISTENER_LOOKUP = {
    'tcp': TCPListener,
    'udp': UDPListener,
    '*': UDPListener  # default listener
}

if HAS_KAFKA:
    LISTENER_LOOKUP['kafka'] = KafkaListener

def get_listener(name):
    '''
    Return the listener class.
    '''
    return LISTENER_LOOKUP.get(name, LISTENER_LOOKUP['*'])

__all__ = (
    'get_listener',
)
