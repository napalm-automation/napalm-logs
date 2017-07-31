# -*- coding: utf-8 -*-
'''
Python 2-3 compatibility.
'''
from __future__ import absolute_import
from __future__ import unicode_literals

import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY3:
    string_type = str
    text_type = str
    binary_type = bytes
else:
    string_type = basestring  # noqa
    text_type = unicode  # noqa
    binary_type = str
