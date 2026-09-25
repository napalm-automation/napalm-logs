# -*- coding: utf-8 -*-
"""
napalm-logs package init
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import os
from importlib.metadata import version, PackageNotFoundError

# For metrics collection, the prometheus_client library
# requires that the env var `prometheus_multiproc_dir`
# be set before start up. At startup, it doesn't matter
# what the value is, and we always overwrite it to either
# the poperly defined default or the user propvided value.
os.environ["prometheus_multiproc_dir"] = "/tmp/napalm_logs_metrics"

# Import napalm-logs pkgs
from napalm_logs.base import NapalmLogs  # noqa: E402

try:
    __version__ = version("napalm-logs")
except PackageNotFoundError:
    __version__ = "Not installed"


__all__ = ("NapalmLogs", "__version__")
