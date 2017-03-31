# -*- coding: utf-8 -*-
'''
Config defaults.
'''
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import logging

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

BUFFER_SIZE = 1024

DEFAULT_DELIM = '/'

VALID_CONFIG = {
    'prefix': {
        'values': {
            'error': basestring
        },
        'line': basestring
    },
    'messages': {
        '*': {
            'values': dict,
            'line': basestring,
            'model': basestring,
            'mapping': dict
        }
    }
}
