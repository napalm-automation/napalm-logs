# -*- coding: utf-8 -*-
'''
Config defaults.
'''
from __future__ import absolute_import

import os
import logging
import napalm_logs.ext.six as six

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
AUTH_MAX_TRY = 5
AUTH_TIMEOUT = 1
LOG_LEVEL = 'warning'
LOG_FORMAT = '%(asctime)s,%(msecs)03.0f [%(name)-17s][%(levelname)-8s] %(message)s'
LOG_FILE = os.path.join(ROOT_DIR, 'var', 'log', 'napalm', 'logs')
LOG_FILE_CLI_OPTIONS = ('cli', 'screen')
# Allowed names for the init files.
OS_INIT_FILENAMES = (
    '__init__',
    'init',
    'index'
)
# The name of the function to be invoked when extracting the parts from the
#   raw syslog message.
INIT_RUN_FUN = 'extract'
# The name of the function to be invoked when the OpenConfig / IETF object
#   is generated.
CONFIG_RUN_FUN = 'emit'

UNKNOWN_DEVICE_NAME = 'unknown'
LISTENER_OPTS = {
    'kafka_topic': 'syslog.net'
}
LOGGER_OPTS = {
    'kafka_topic': 'syslog.net.processed',
    'send_raw': False,  # initially called `syslog`
    'send_unknown': False
}
PUBLISHER_OPTS = {
    'kafka_topic': 'napalm-logs',
    'send_raw': False,
    'send_unknown': False
}

LOGGING_LEVEL = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

VALID_CONFIG = {
    'prefixes': [
        {
            'values': {
                'tag': six.string_type
            },
            'line': six.string_type
        }
    ],
    'messages': [
        {
            # 'error' should be unique and vendor agnostic.
            # Currently we are using the JUNOS syslog message name as the canonical name.
            # This may change if we are able to find a more well defined naming system.
            'error': six.string_type,
            'tag': six.string_type,
            'values': dict,
            'replace': dict,
            'line': six.string_type,
            'model': six.string_type,
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
AUTH_KEEP_ALIVE = b'KEEPALIVE'
AUTH_KEEP_ALIVE_ACK = b'KEEPALIVEACK'
AUTH_KEEP_ALIVE_INTERVAL = 10
AUTH_MAX_CONN = 5
AUTH_TIMEOUT = 5
MAGIC_ACK = b'ACK'
MAGIC_REQ = b'INIT'
AUTH_CIPHER = 'ECDHE-RSA-AES256-GCM-SHA384'

OPEN_CONFIG_NO_MODEL = 'NO_MODEL'

# replacement lambdas
REPLACEMENTS = {
    'uppercase': lambda var: var.upper(),
    'lowercase': lambda var: var.lower(),
    'color_to_severity': lambda var: _COLOR_TO_severity.get(var, 0)
}

# For use with replacement lamdas
_COLOR_TO_severity = {
    'RED': 3,
    'YELLOW': 4
    }
