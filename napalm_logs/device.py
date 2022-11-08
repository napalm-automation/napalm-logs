# -*- coding: utf-8 -*-
"""
Device worker process
"""
from __future__ import absolute_import

# Import python stdlib
import os
import re
import signal
import logging
import calendar
import datetime
import dateutil
import threading

# Import thrid party libs
import zmq
import umsgpack
import dateparser
from prometheus_client import Counter

# Import napalm-logs pkgs
import napalm_logs.utils
from napalm_logs.proc import NapalmLogsProc
from napalm_logs.config import PUB_PX_IPC_URL
from napalm_logs.config import DEV_IPC_URL

# exceptions
from napalm_logs.exceptions import NapalmLogsExit

log = logging.getLogger(__name__)


class NapalmLogsDeviceProc(NapalmLogsProc):
    """
    Device sub-process class.
    """

    def __init__(self, name, opts, config):
        self._name = name
        log.debug("Starting process for %s", self._name)
        self._config = config
        self.opts = opts
        self.__up = False
        self.compiled_messages = None
        self._compile_messages()

    def _exit_gracefully(self, signum, _):
        log.debug("Caught signal in %s device process", self._name)
        self.stop()

    def _setup_ipc(self):
        """
        Subscribe to the right topic
        in the device IPC and publish to the
        publisher proxy.
        """
        self.ctx = zmq.Context()
        # subscribe to device IPC
        log.debug("Creating the dealer IPC for %s", self._name)
        self.sub = self.ctx.socket(zmq.DEALER)
        self.sub.setsockopt(zmq.IDENTITY, bytes(self._name, "utf-8"))
        self.sub.setsockopt(zmq.RCVHWM, self.opts["hwm"])
        # subscribe to the corresponding IPC pipe
        self.sub.connect(DEV_IPC_URL)
        # publish to the publisher IPC
        self.pub = self.ctx.socket(zmq.PUB)
        self.pub.connect(PUB_PX_IPC_URL)
        self.pub.setsockopt(zmq.SNDHWM, self.opts["hwm"])

    def _compile_messages(self):
        """
        Create a list of all OS messages and their compiled regexs
        """
        self.compiled_messages = []
        if not self._config:
            return
        for message_dict in self._config.get("messages", {}):
            error = message_dict["error"]
            tag = message_dict["tag"]
            model = message_dict["model"]
            match_on = message_dict.get("match_on", "tag")
            if "__python_fun__" in message_dict:
                self.compiled_messages.append(
                    {
                        "error": error,
                        "tag": tag,
                        "match_on": match_on,
                        "model": model,
                        "__python_fun__": message_dict["__python_fun__"],
                    }
                )
                continue
            values = message_dict["values"]
            line = message_dict["line"]
            mapping = message_dict["mapping"]
            # We will now figure out which position each value is in so we can use it with the match statement
            position = {}
            replace = {}
            for key in list(values.keys()):
                if "|" in key:
                    new_key, replace[new_key] = key.replace(" ", "").split("|")
                    values[new_key] = values.pop(key)
                    key = new_key
                position[line.find("{" + key + "}")] = key
            sorted_position = {}
            for i, elem in enumerate(sorted(position.items())):
                sorted_position[elem[1]] = i + 1
            # Escape the line, then remove the escape for the curly bracets so they can be used when formatting
            escaped = re.escape(line).replace(r"\{", "{").replace(r"\}", "}")
            # Replace a whitespace with \s+
            escaped = escaped.replace(r"\ ", r"\s+")
            self.compiled_messages.append(
                {
                    "error": error,
                    "tag": tag,
                    "match_on": match_on,
                    "line": re.compile(escaped.format(**values)),
                    "positions": sorted_position,
                    "values": values,
                    "replace": replace,
                    "model": model,
                    "mapping": mapping,
                    "state": message_dict.get("state"),
                    "state_tag": message_dict.get("state_tag"),
                }
            )
        log.debug("Compiled messages:")
        log.debug(self.compiled_messages)

    def _parse(self, msg_dict):
        """
        Parse a syslog message and check what OpenConfig object should
        be generated.
        """
        error_present = False
        # log.debug('Matching the message:')
        # log.debug(msg_dict)
        for message in self.compiled_messages:
            # log.debug('Matching using:')
            # log.debug(message)
            match_on = message["match_on"]
            if match_on not in msg_dict:
                # log.debug('%s is not a valid key in the partially parsed dict', match_on)
                continue
            if message["tag"] != msg_dict[match_on]:
                continue
            if "__python_fun__" in message:
                return {
                    "model": message["model"],
                    "error": message["error"],
                    "__python_fun__": message["__python_fun__"],
                }
            error_present = True
            match = message["line"].search(msg_dict["message"])
            if not match:
                continue
            positions = message.get("positions", {})
            values = message.get("values")
            ret = {
                "model": message["model"],
                "mapping": message["mapping"],
                "replace": message["replace"],
                "error": message["error"],
                "_state": message["state"],
                "_state_tag": message["state_tag"],
            }
            for key in values.keys():
                # Check if the value needs to be replaced
                if key in message["replace"]:
                    result = napalm_logs.utils.cast(
                        match.group(positions.get(key)), message["replace"][key]
                    )
                else:
                    result = match.group(positions.get(key))
                ret[key] = result
            return ret
        if error_present is True:
            log.info(
                "Configured regex did not match for os: %s tag %s",
                self._name,
                msg_dict.get("tag", ""),
            )
        else:
            log.info(
                "Syslog message not configured for os: %s tag %s",
                self._name,
                msg_dict.get("tag", ""),
            )

    def _emit(self, **kwargs):
        """
        Emit an OpenConfig object given a certain combination of
        fields mappeed in the config to the corresponding hierarchy.
        """
        oc_dict = {}
        for mapping, result_key in kwargs["mapping"]["variables"].items():
            result = kwargs[result_key]
            oc_dict = napalm_logs.utils.setval(
                mapping.format(**kwargs), result, oc_dict
            )
        for mapping, result in kwargs["mapping"]["static"].items():
            oc_dict = napalm_logs.utils.setval(
                mapping.format(**kwargs), result, oc_dict
            )

        return oc_dict

    def _publish(self, obj):
        """
        Publish the OC object.
        """
        bin_obj = umsgpack.packb(obj)
        self.pub.send(bin_obj)

    def _format_time(self, time, date, timezone, prefix_id):
        date_time = None
        if time and date:
            date_time = dateparser.parse("{} {}".format(date, time))
        if not date_time:
            tz = dateutil.tz.gettz(timezone)
            date_time = datetime.datetime.now(tz)
        return int(calendar.timegm(date_time.utctimetuple()))

    def start(self):
        """
        Start the worker process.
        """
        # metrics
        napalm_logs_device_messages_received = Counter(
            "napalm_logs_device_messages_received",
            "Count of messages received by the device process",
            ["device_os"],
        )
        napalm_logs_device_raw_published_messages = Counter(
            "napalm_logs_device_raw_published_messages",
            "Count of raw type published messages",
            ["device_os"],
        )
        napalm_logs_device_published_messages = Counter(
            "napalm_logs_device_published_messages",
            "Count of published messages",
            ["device_os"],
        )
        napalm_logs_device_oc_object_failed = Counter(
            "napalm_logs_device_oc_object_failed",
            "Counter of failed OpenConfig object generations",
            ["device_os"],
        )
        if self.opts.get("metrics_include_attributes", True):
            napalm_logs_device_published_messages_attrs = Counter(
                "napalm_logs_device_published_messages_attrs",
                "Counter of published messages, with more granular selection",
                ["device_os", "host", "error"],
            )
        self._setup_ipc()
        # Start suicide polling thread
        thread = threading.Thread(
            target=self._suicide_when_without_parent, args=(os.getppid(),)
        )
        thread.start()
        signal.signal(signal.SIGTERM, self._exit_gracefully)
        self.__up = True
        while self.__up:
            # bin_obj = self.sub.recv()
            # msg_dict, address = umsgpack.unpackb(bin_obj, use_list=False)
            try:
                bin_obj = self.sub.recv()
                msg_dict, address = umsgpack.unpackb(bin_obj, use_list=False)
            except zmq.ZMQError as error:
                if self.__up is False:
                    log.info("Exiting on process shutdown [%s]", self._name)
                    return
                else:
                    raise NapalmLogsExit(error)
            log.debug(
                "%s: dequeued %s, received from %s", self._name, msg_dict, address
            )
            napalm_logs_device_messages_received.labels(device_os=self._name).inc()
            host = msg_dict.get("host")
            prefix_id = msg_dict.pop("__prefix_id__")
            if "timestamp" in msg_dict:
                timestamp = msg_dict.pop("timestamp")
            else:
                timestamp = self._format_time(
                    msg_dict.get("time", ""),
                    msg_dict.get("date", ""),
                    msg_dict.get("timeZone", "UTC"),
                    prefix_id,
                )
            facility = msg_dict.get("facility")
            severity = msg_dict.get("severity")

            kwargs = self._parse(msg_dict)
            if not kwargs:
                # Unable to identify what model to generate for the message in cause.
                # But publish the message when the user requested to push raw messages.
                to_publish = {
                    "ip": address,
                    "host": host,
                    "timestamp": timestamp,
                    "message_details": msg_dict,
                    "os": self._name,
                    "error": "RAW",
                    "model_name": "raw",
                    "facility": facility,
                    "severity": severity,
                }
                log.debug("Queueing to be published:")
                log.debug(to_publish)
                # self.pub_pipe.send(to_publish)
                self.pub.send(umsgpack.packb(to_publish))
                napalm_logs_device_raw_published_messages.labels(
                    device_os=self._name
                ).inc()
                continue
            try:
                if "__python_fun__" in kwargs:
                    log.debug(
                        "Using the Python parser to determine the YANG-equivalent object"
                    )
                    yang_obj = kwargs["__python_fun__"](msg_dict)
                else:
                    yang_obj = self._emit(**kwargs)
            except Exception:
                log.exception(
                    "Unexpected error when generating the OC object.", exc_info=True
                )
                napalm_logs_device_oc_object_failed.labels(device_os=self._name).inc()
                continue
            log.debug("Generated OC object:")
            log.debug(yang_obj)
            error = kwargs.get("error")
            model_name = kwargs.get("model")
            to_publish = {
                "error": error,
                "host": host,
                "ip": address,
                "timestamp": timestamp,
                "yang_message": yang_obj,
                "message_details": msg_dict,
                "yang_model": model_name,
                "os": self._name,
                "facility": facility,
                "severity": severity,
            }
            if kwargs.get("_state") is not None:
                to_publish["state"] = kwargs["_state"]
                if kwargs.get("_state_tag"):
                    to_publish["state_tag"] = kwargs["_state_tag"]
            log.debug("Queueing to be published:")
            log.debug(to_publish)
            # self.pub_pipe.send(to_publish)
            self.pub.send(umsgpack.packb(to_publish))
            # self._publish(to_publish)
            napalm_logs_device_published_messages.labels(device_os=self._name).inc()
            if self.opts.get("metrics_include_attributes", True):
                napalm_logs_device_published_messages_attrs.labels(
                    device_os=self._name,
                    error=to_publish["error"],
                    host=to_publish["host"],
                ).inc()

    def stop(self):
        """
        Stop the worker process.
        """
        log.info("Stopping %s device process", self._name)
        self.__up = False
        self.sub.close()
        self.pub.close()
        self.ctx.term()
        # self.pipe.close()
        # self.pub_pipe.close()
