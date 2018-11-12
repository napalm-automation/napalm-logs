# -*- coding: utf-8 -*-
'''
HTTP(s) transport for napalm-logs.
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import stdlib
import umsgpack
import logging

try:
    from prometheus_client import Gauge, Counter
    from prometheus_client import start_http_server, CollectorRegistry, multiprocess
    HAS_PROMETHEUS_CLIENT = True
except ImportError:
    HAS_PROMETHEUS_CLIENT = False

# Import napalm-logs pkgs
from napalm_logs.transport.base import TransportBase

log = logging.getLogger(__name__)


class PrometheusTransport(TransportBase):
    '''
    Prometheus transport class.
    '''
    NO_ENCRYPT = True
    # This tells the publisher to not encrypt the messages
    #   published over this channel.

    def __init__(self, address, port, **kwargs):
        if kwargs.get('address'):
            self.address = kwargs['address']
        else:
            self.address = address
        if not self.address:
            self.address = ''
        if kwargs.get('port'):
            self.port = kwargs['port']
        else:
            self.port = port
        log.error('Prometheus publisher %s:%d', self.address, self.port)

    def start(self):
        log.info('Starting the Prometheus publisher...')
        self.metrics = {
            'napalm_logs': [
                Counter('napalm_logs_published_messages',
                        'Number of published napalm-logs messages',
                        ['host', 'os', 'severity', 'facility', 'error'])
            ],
            'BGP_MD5_INCORRECT': [
                Counter('BGP_MD5_INCORRECT_counter',
                        'Number of MD5 incorrect notifications',
                        ['host', 'os', 'neighbor'])
            ],
            'BGP_PREFIX_LIMIT_EXCEEDED': [
                Gauge('BGP_PREFIX_LIMIT_EXCEEDED_gauge',
                      'Count of prefixes received when the BGP limit has been exceeded',
                      ['host', 'os', 'neighbor', 'asn']),
                Counter('BGP_PREFIX_LIMIT_EXCEEDED_counter',
                        'Count of notifications received for BGP_PREFIX_LIMIT_EXCEEDED',
                        ['host', 'os', 'neighbor', 'asn'])
            ]
        }
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
        start_http_server(self.port, addr=self.address, registry=registry)

    def publish(self, obj):
        obj = umsgpack.unpackb(obj)
        labels = [
            obj['host'],
            obj['os']
        ]
        err = obj['error']
        if obj['error'] == 'BGP_MD5_INCORRECT':
            neighbor = list(obj['yang_message']['bgp']['neighbors']['neighbor'].keys())[0]
            labels.append(neighbor)
            self.metrics[err][0].labels(*labels).inc()
        elif obj['error'] == 'BGP_PREFIX_LIMIT_EXCEEDED':
            neighbor_dict = obj['yang_message']['bgp']['neighbors']['neighbor']
            neighbor = list(neighbor_dict.keys())[0]
            asn = neighbor_dict[neighbor]['state']['peer_as']
            labels.extend([
                neighbor,
                asn
            ])
            afi = 'inet' if '.' in neighbor else 'inet6'
            try:
                received = neighbor_dict[neighbor]['afi_safis']['afi_safi'][afi]['state']['prefixes']['received']
            except KeyError:
                log.info('Unable to determine the received prefixes for %s', neighbor)
            else:
                self.metrics[err][0].labels(*labels).set(received)
            self.metrics[err][1].labels(*labels).inc()

    def stop(self):
        log.info('Exiting the Prometheus publisher...')
