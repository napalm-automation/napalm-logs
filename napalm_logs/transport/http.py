# -*- coding: utf-8 -*-
'''
HTTP(s) transport for napalm-logs.
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import stdlib
import logging
import threading

# Import third party libs
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import tornado
    HAS_TORNADO = True
except ImportError:
    HAS_TORNADO = False

# Import napalm-logs pkgs
import napalm_logs.utils
from napalm_logs.exceptions import TransportException
from napalm_logs.transport.base import TransportBase

log = logging.getLogger(__name__)


class HTTPTransport(TransportBase):
    '''
    HTTP transport class.
    '''
    NO_ENCRYPT = True 
    # This tells the publisher to not encrypt the messages
    #   published over this channel.

    def __init__(self, address, port, **kwargs):
        if kwargs.get('address'):
            self.address = kwargs['address']
        else:
            self.address = address
        self.method = kwargs.get('method', 'GET')
        log.debug('Publishing to %s using %s', self.address, self.method)
        self.auth = kwargs.get('auth')
        username = kwargs.get('username')
        password = kwargs.get('password')
        if not self.auth:
            if username and password:
                self.auth = (username, password)
        self.headers = kwargs.get('headers', {})
        self.verify_ssl = kwargs.get('verify_ssl', True)
        self.params = kwargs.get('params')
        self.backend = kwargs.get('backend')
        if not self.backend:
            log.debug('No explicit backend requested')
            if HAS_TORNADO:
                self.backend = 'tornado'
                log.debug('Executing asynchronous requests using Tornado')
            elif HAS_REQUESTS:
                self.backend = 'requests'
                log.debug('Excuting threaded requests')

    def start(self):
        # Nothing in particular to prepare
        if self.backend not in ('requests', 'tornado'):
            raise TransportException('Invalid HTTP backend')

    def publish(self, obj):
        data = napalm_logs.utils.unserialize(obj)
        if self.backend == 'tornado':
            pass
        elif self.backend == 'requests':
            thread = threading.Thread(target=self._publish_requests,
                                      args=(data,))
            thread.daemon = True
            thread.start()

    def _publish_requests(self, data):
        session = requests.Session()
        session.auth = self.auth
        session.headers.update(self.headers)
        session.verify = self.verify_ssl
        result = session.request(
            self.method,
            self.address,
            params=self.params,
            data=data
        )
        if not result.ok:
            log.error('Unable to publish to %s', self.address)
            log.error('Status code: %d', result.status_code)
            log.error(result.text)
        else:
            log.debug(result.text)

    def _handle_tornado_response(self, response):
        if response.error:
            log.error('Unable to push to %s', self.address)
            log.error(response.error)
        else:
            log.debug(response.body)

    def stop(self):
        # Nothing in particular to shutdown
        return
