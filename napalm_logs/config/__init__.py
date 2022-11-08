# -*- coding: utf-8 -*-
"""
Config defaults.
"""
from __future__ import absolute_import

import os
import tempfile
import logging

# config
ROOT_DIR = "/"
CONFIG_FILE = os.path.join(ROOT_DIR, "etc", "napalm", "logs")
ADDRESS = "0.0.0.0"
PORT = 514
LISTENER = "udp"
LOGGER = None
PUBLISHER = "zmq"
MAX_TCP_CLIENTS = 5
PUBLISH_ADDRESS = "0.0.0.0"
PUBLISH_PORT = 49017
AUTH_ADDRESS = "0.0.0.0"
AUTH_PORT = 49018
AUTH_MAX_TRY = 5
AUTH_TIMEOUT = 1
SERIALIZER = "msgpack"
LOG_LEVEL = "warning"
LOG_FORMAT = "%(asctime)s,%(msecs)03.0f [%(name)-17s][%(levelname)-8s] %(message)s"
LOG_FILE = os.path.join(ROOT_DIR, "var", "log", "napalm", "logs")
LOG_FILE_CLI_OPTIONS = ("cli", "screen")
ZMQ_INTERNAL_HWM = 1000
METRICS_ADDRESS = "0.0.0.0"
METRICS_PORT = 9443
METRICS_DIR = "/tmp/napalm_logs_metrics"
BUFFER_EXPIRE_TIME = 5

# Allowed names for the init files.
OS_INIT_FILENAMES = ("__init__", "init", "index")
# The name of the function to be invoked when extracting the parts from the
#   raw syslog message.
INIT_RUN_FUN = "extract"
# The name of the function to be invoked when the OpenConfig / IETF object
#   is generated.
CONFIG_RUN_FUN = "emit"

UNKNOWN_DEVICE_NAME = "unknown"

LISTENER_OPTS = {}

LOGGER_OPTS = {"send_raw": False, "send_unknown": False}

PUBLISHER_OPTS = {"send_raw": False, "send_unknown": False}

LOGGING_LEVEL = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

VALID_CONFIG = {
    "prefixes": [{"values": {"tag": str}, "line": str}],
    "messages": [
        {
            # 'error' should be unique and vendor agnostic.
            # Currently we are using the JUNOS syslog message name as the canonical name.
            # This may change if we are able to find a more well defined naming system.
            "error": str,
            "tag": str,
            "values": dict,
            "line": str,
            "model": str,
            "mapping": {"variables": dict, "static": dict},
        }
    ],
}

# listener
BUFFER_SIZE = 1024
REUSE_PORT = False
TIMEOUT = 60

# device
DEFAULT_DELIM = "//"

# proc
PROC_DEAD_FLAGS = ("T", "X", "Z")

# zmq proxies
TMP_DIR = tempfile.gettempdir()
AUTH_IPC_URL = "ipc://{}".format(os.path.join(TMP_DIR, "napalm-logs-auth"))
# the auth proxy is not used yet, TODO
LST_IPC_URL = "ipc://{}".format(os.path.join(TMP_DIR, "napalm-logs-lst"))
SRV_IPC_URL = "ipc://{}".format(os.path.join(TMP_DIR, "napalm-logs-srv"))
# the publisher IPC is used as proxy
# the devices send the messages to the proxy
# and the publisher subscribes to the proxy and
# publishes them on the desired transport
DEV_IPC_URL = "ipc://{}".format(os.path.join(TMP_DIR, "napalm-logs-dev"))
# the server publishes to a separate IPC per device
PUB_PX_IPC_URL = "ipc://{}".format(os.path.join(TMP_DIR, "napalm-logs-pub-px"))
PUB_IPC_URL = "ipc://{}".format(os.path.join(TMP_DIR, "napalm-logs-pub"))

# auth
AUTH_KEEP_ALIVE = b"KEEPALIVE"
AUTH_KEEP_ALIVE_ACK = b"KEEPALIVEACK"
AUTH_KEEP_ALIVE_INTERVAL = 10
AUTH_MAX_CONN = 5
AUTH_TIMEOUT = 5
MAGIC_ACK = b"ACK"
MAGIC_REQ = b"INIT"
AUTH_CIPHER = "ECDHE-RSA-AES256-GCM-SHA384"

OPEN_CONFIG_NO_MODEL = "NO_MODEL"
