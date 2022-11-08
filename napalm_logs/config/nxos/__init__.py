# -*- coding: utf-8 -*-
"""
Prefix profiler for Nexus devices.
This profiler matches messages having the following form:

sw01.bjm01: 2017 Jul 26 14:42:46 UTC: %AUTHPRIV-6-SYSTEM_MSG: pam_unix(dcos_sshd:session): session opened for user luke by (uid=0) - dcos_sshd[12977]  # noqa
"""
from collections import OrderedDict

import napalm_logs.utils

_RGX_PARTS = [
    ("pri", r"(\d+)"),
    ("host", r"([^ ]+)"),
    ("date", r"(\d+ \w+ +\d+)"),
    ("time", r"(\d\d:\d\d:\d\d)"),
    ("timeZone", r"(\w\w\w)"),
    ("tag", r"([\w\d-]+)"),
    ("message", r"(.*)"),
]
_RGX_PARTS = OrderedDict(_RGX_PARTS)
_RGX = r"\<{0[pri]}\>{0[host]}: {0[date]} {0[time]} {0[timeZone]}: %{0[tag]}: {0[message]}".format(
    _RGX_PARTS
)

_ALT_RGX_PARTS = [
    ("pri", r"(\d+)"),
    ("date", r"(\d+ \w+ +\d+)"),
    ("time", r"(\d\d:\d\d:\d\d)"),
    ("host", r"([^ ]+)"),
    ("tag", r"([\w\d-]+)"),
    ("message", r"(.*)"),
]
_ALT_RGX_PARTS = OrderedDict(_ALT_RGX_PARTS)
_ALT_RGX = r"\<{0[pri]}\>{0[date]} {0[time]} {0[host]} %{0[tag]}: {0[message]}".format(
    _ALT_RGX_PARTS
)

_TIME_FORMAT = ("{date} {time} {timeZone}", "%Y %b %d %H:%M:%S %Z")
_ALT_TIME_FORMAT = ("{date} {time}", "%Y %b %d %H:%M:%S")


def extract(msg):
    return napalm_logs.utils.extract(
        _RGX, msg, _RGX_PARTS, _TIME_FORMAT
    ) or napalm_logs.utils.extract(_ALT_RGX, msg, _ALT_RGX_PARTS, _ALT_TIME_FORMAT)
