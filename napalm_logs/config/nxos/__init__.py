# -*- coding: utf-8 -*-
'''
Prefix profiler for Nexus devices.
This profiler matches messages having the following form:

sw01.bjm01: 2017 Jul 26 14:42:46 UTC: %AUTHPRIV-6-SYSTEM_MSG: pam_unix(dcos_sshd:session): session opened for user luke by (uid=0) - dcos_sshd[12977]
'''
import re
from collections import OrderedDict

_RGX_PARTS = [
    ('host', r'([^ ]+)'),
    ('date', r'(\d+ \w+ +\d+)'),
    ('time', r'(\d\d:\d\d:\d\d)'),
    ('timeZone', r'(\w\w\w)'),
    ('tag', r'([\w\d-]+)'),
    ('message', r'(.*)')
]
_RGX_PARTS = OrderedDict(_RGX_PARTS)

_RGX = '{0[host]}: {0[date]} {0[time]} {0[timeZone]}: %{0[tag]}: {0[message]}'.format(_RGX_PARTS)


def extract(msg):
    ret = {}
    matched = re.search(_RGX, msg)
    if not matched:
        return None
    else:
        group_index = 0
        for group_value in matched.groups():
            group_name = _RGX_PARTS.keys()[group_index]
            ret[group_name] = group_value
            group_index += 1
    return ret
