# -*- coding: utf-8 -*-
'''
Config defaults.
'''
from __future__ import absolute_import
from __future__ import unicode_literals

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
