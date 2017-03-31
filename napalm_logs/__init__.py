# -*- coding: utf-8 -*-
'''
napalm-logs package init
'''
from __future__ import absolute_import
from __future__ import unicode_literals

import pkg_resources

# Import napalm-logs pkgs
from napalm_logs.base import NapalmLogs

try:
    __version__ = pkg_resources.get_distribution('napalm-logs').version
except pkg_resources.DistributionNotFound:
    __version__ = "Not installed"


__all__ = ('NapalmLogs', '__version__')
