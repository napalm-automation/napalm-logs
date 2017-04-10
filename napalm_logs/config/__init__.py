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
PUBLISH_ADDRESS = '0.0.0.0'
PUBLISH_PORT = 49017
LOG_LEVEL = 'warning'
LOG_FORMAT = '%(asctime)s,%(msecs)03.0f [%(name)-17s][%(levelname)-8s] %(message)s'
LOG_FILE = os.path.join(ROOT_DIR, 'var', 'log', 'napalm', 'logs')
LOG_FILE_CLI_OPTIONS = ('cli', 'screen')

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
            'line': basestring,
            'model': basestring,
            'mapping': dict
        }
    ]
}

# listener
BUFFER_SIZE = 1024

# device
DEFAULT_DELIM = '/'

# auth
AUTH_MAX_CONN = 5
AUTH_TIMEOUT = 5
AUTH_CIPHER = 'ECDHE-ECDSA-AES256-CCM8'
MAGIC_ACK = 'ACK'
MAGIC_REQ = 'INIT'
AES_BS = 32  # AES block size
# must be 16 or 32 bytes long
