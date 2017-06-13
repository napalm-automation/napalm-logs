# -*- coding: utf-8 -*-
'''
Config defaults.
'''
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import logging

# config
ROOT_DIR = '/'
CONFIG_FILE = os.path.join(ROOT_DIR, 'etc', 'napalm', 'logs')
ADDRESS = '0.0.0.0'
PORT = 514
LISTENER = 'udp'
PUBLISH_ADDRESS = '0.0.0.0'
PUBLISH_PORT = 49017
AUTH_ADDRESS = '0.0.0.0'
AUTH_PORT = 49018
LOG_LEVEL = 'warning'
LOG_FORMAT = '%(asctime)s,%(msecs)03.0f [%(name)-17s][%(levelname)-8s] %(message)s'
LOG_FILE = os.path.join(ROOT_DIR, 'var', 'log', 'napalm', 'logs')
LOG_FILE_CLI_OPTIONS = ('cli', 'screen')
KAFKA_LISTENER_TOPIC = "syslog.net"
KAFKA_PUBLISHER_TOPIC = "napalm-logs"

LOGGING_LEVEL = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

VALID_CONFIG = {
    'prefix': {
        'values': {
            'tag': basestring
        },
        'line': basestring
    },
    'messages': [
        {
            # 'error' should be unique and vendor agnostic. Currently we are using the JUNOS syslog message name as the canonical name.
            # This may change if we are able to find a more well defined naming system.
            'error': basestring,
            'tag': basestring,
            'values': dict,
            'replace': dict,
            'line': basestring,
            'model': basestring,
            'mapping': {
                'variables': dict,
                'static': dict
            }
        }
    ]
}

# listener
BUFFER_SIZE = 1024
TIMEOUT = 60

# device
DEFAULT_DELIM = '//'

# proc
PROC_DEAD_FLAGS = ('T', 'X', 'Z')

# zmq proxies
AUTH_IPC_URL = 'ipc:///tmp/napalm-logs-auth'
# the auth proxy is not used yet, TODO
LST_IPC_URL = 'ipc:///tmp/napalm-logs-lst'
SRV_IPC_URL = 'ipc:///tmp/napalm-logs-srv'
# the publisher IPC is used as proxy
# the devices send the messages to the proxy
# and the publisher subscribes to the proxy and
# publishes them on the desired transport
DEV_IPC_URL_TPL = 'ipc:///tmp/napalm-logs-dev-{os}'
# the server publishes to a separate IPC per device
PUB_IPC_URL = 'ipc:///tmp/napalm-logs-pub'

# auth
AUTH_MAX_CONN = 5
AUTH_TIMEOUT = 5
MAGIC_ACK = 'ACK'
MAGIC_REQ = 'INIT'
AUTH_CIPHER = 'ECDHE-RSA-AES256-GCM-SHA384'

# replacement lambdas
REPLACEMENTS = {
    'uppercase': lambda var: var.upper(),
    'lowercase': lambda var: var.lower()
}
