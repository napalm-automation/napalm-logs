# -*- coding: utf-8 -*-
'''
Kafka listener for napalm-logs.
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import stdlib
import json
import time
import signal
import logging

# Import third party libs
try:
    import kafka
    HAS_KAFKA = True
except ImportError as err:
    HAS_KAFKA = False

# Import napalm-logs pkgs
from napalm_logs.listener.base import ListenerBase
from napalm_logs.exceptions import ListenerException

log = logging.getLogger(__name__)


class KafkaListener(ListenerBase):
    '''
    Kafka listener class.
    '''
    def __init__(self, address, port, pipe, **kwargs):
        self.pipe = pipe
        self.__up = False
        if kwargs.get('address'):
            address = kwargs['address']
        if kwargs.get('port'):
            address = kwargs['port']
        if kwargs.get('bootstrap_servers'):
            self.bootstrap_servers = kwargs['bootstrap_servers']
        else:
            self.bootstrap_servers = '{}:{}'.format(address, port)
        self.kafka_topic = kwargs['kafka_topic']

    def _exit_gracefully(self, signum, _):
        log.debug('Caught signal in listener process')
        self.stop()

    def start(self):
        '''
        Start listening for messages
        '''
        # Start suicide polling thread
        signal.signal(signal.SIGTERM, self._exit_gracefully)
        self.__up = True
        try:
            self.consumer = kafka.KafkaConsumer(bootstrap_servers=self.bootstrap_servers,
                                                group_id='napalm-logs')
        except kafka.errors.NoBrokersAvailable as err:
            log.error(err, exc_info=True)
            raise ListenerException(err)
        self.consumer.subscribe(topics=[self.kafka_topic])
        while self.__up:
            try:
                msg = next(self.consumer)
            except ValueError as error:
                if self.__up is False:
                    return
                else:
                    msg = 'Received kafka error: {}'.format(error)
                    log.error(msg, exc_info=True)
                    raise NapalmLogsExit(msg)
            log_source = msg.key
            decoded = json.loads(msg.value)
            log_message = decoded.get('message')
            log.debug('[{2}] Received {0} from {1}. Adding in the queue'.format(log_message, log_source, time.time()))
            self.pipe.send((log_message, log_source))

    def stop(self):
        log.info('Stopping listener process')
        self.__up = False
        self.consumer.unsubscribe()
        self.consumer.close()
        self.pipe.close()
