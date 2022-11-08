# -*- coding: utf-8 -*-
"""
Listener worker process
"""
from __future__ import absolute_import

# Import pythond stdlib
import os
import signal
import logging
import threading

# Import third party libs
import zmq
import umsgpack
import nacl.utils
import nacl.secret
from prometheus_client import Counter

# Import napalm-logs pkgs
import napalm_logs.utils
from napalm_logs.config import PUB_IPC_URL
from napalm_logs.config import SERIALIZER
from napalm_logs.proc import NapalmLogsProc
from napalm_logs.transport import get_transport
from napalm_logs.serializer import get_serializer

# exceptions
from napalm_logs.exceptions import NapalmLogsExit

log = logging.getLogger(__name__)


class NapalmLogsPublisherProc(NapalmLogsProc):
    """
    publisher sub-process class.
    """

    def __init__(
        self,
        opts,
        address,
        port,
        transport_type,
        serializer,
        private_key,
        signing_key,
        publisher_opts,
        disable_security=False,
        pub_id=None,
    ):
        self.__up = False
        self.opts = opts
        self.pub_id = pub_id
        self.address = publisher_opts.pop("address", None) or address
        self.port = publisher_opts.pop("port", None) or port
        log.debug("Publishing to %s:%d", self.address, self.port)
        self.serializer = publisher_opts.get("serializer") or serializer
        self.default_serializer = self.serializer == SERIALIZER
        self.disable_security = publisher_opts.get("disable_security", disable_security)
        self._transport_type = transport_type
        self.publisher_opts = publisher_opts
        self.error_whitelist = publisher_opts.get("error_whitelist", [])
        self.error_blacklist = publisher_opts.get("error_blacklist", [])
        if not disable_security:
            self.__safe = nacl.secret.SecretBox(private_key)
            self.__signing_key = signing_key
        self._strip_message_details = publisher_opts.pop("strip_message_details", False)
        self._setup_transport()

    def _exit_gracefully(self, signum, _):
        log.debug("Caught signal in publisher process")
        self.stop()

    def _setup_ipc(self):
        """
        Subscribe to the pub IPC
        and publish the messages
        on the right transport.
        """
        self.ctx = zmq.Context()
        log.debug(
            "Setting up the %s publisher subscriber #%d",
            self._transport_type,
            self.pub_id,
        )
        self.sub = self.ctx.socket(zmq.SUB)
        self.sub.connect(PUB_IPC_URL)
        self.sub.setsockopt(zmq.SUBSCRIBE, b"")
        self.sub.setsockopt(zmq.RCVHWM, self.opts["hwm"])

    def _setup_transport(self):
        """
        Setup the transport.
        """
        if "RAW" in self.error_whitelist:
            log.info(
                "%s %d will publish partially parsed messages",
                self._transport_type,
                self.pub_id,
            )
        if "UNKNOWN" in self.error_whitelist:
            log.info(
                "%s %d will publish unknown messages", self._transport_type, self.pub_id
            )
        transport_class = get_transport(self._transport_type)
        log.debug(
            "Serializing the object for %s using %s",
            self._transport_type,
            self.serializer,
        )
        self.serializer_fun = get_serializer(self.serializer)
        self.transport = transport_class(self.address, self.port, **self.publisher_opts)
        self.__transport_encrypt = True
        if (
            hasattr(self.transport, "NO_ENCRYPT")
            and getattr(self.transport, "NO_ENCRYPT") is True
        ):
            self.__transport_encrypt = False

    def _prepare(self, serialized_obj):
        """
        Prepare the object to be sent over the untrusted channel.
        """
        # generating a nonce
        nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
        # encrypting using the nonce
        encrypted = self.__safe.encrypt(serialized_obj, nonce)
        # sign the message
        signed = self.__signing_key.sign(encrypted)
        return signed

    def _serialize(self, obj, bin_obj):
        if self.default_serializer:
            # It's just easier to poll a boolean, rather than
            # re-serializing the message.
            # The reasoning why this is needed is because the structured
            # messages are passed anyway serialized between processes,
            # but the user may request a different serializer.
            return bin_obj
        return self.serializer_fun(obj)

    def start(self):
        """
        Listen to messages and publish them.
        """
        # metrics
        napalm_logs_publisher_received_messages = Counter(
            "napalm_logs_publisher_received_messages",
            "Count of messages received by the publisher",
            ["publisher_type", "address", "port"],
        )
        napalm_logs_publisher_whitelist_blacklist_check_fail = Counter(
            "napalm_logs_publisher_whitelist_blacklist_check_fail",
            "Count of messages which fail the whitelist/blacklist check",
            ["publisher_type", "address", "port"],
        )
        napalm_logs_publisher_messages_published = Counter(
            "napalm_logs_publisher_messages_published",
            "Count of published messages",
            ["publisher_type", "address", "port"],
        )
        self._setup_ipc()
        # Start suicide polling thread
        thread = threading.Thread(
            target=self._suicide_when_without_parent, args=(os.getppid(),)
        )
        thread.start()
        signal.signal(signal.SIGTERM, self._exit_gracefully)
        self.transport.start()
        self.__up = True
        while self.__up:
            try:
                bin_obj = self.sub.recv()
            except zmq.ZMQError as error:
                if self.__up is False:
                    log.info("Exiting on process shutdown")
                    return
                else:
                    log.error(error, exc_info=True)
                    raise NapalmLogsExit(error)
            obj = umsgpack.unpackb(bin_obj)
            if self._strip_message_details:
                obj.pop("message_details", None)
                bin_obj = self.serializer_fun(obj)
            napalm_logs_publisher_received_messages.labels(
                publisher_type=self._transport_type,
                address=self.address,
                port=self.port,
            ).inc()
            if not napalm_logs.utils.check_whitelist_blacklist(
                obj["error"],
                whitelist=self.error_whitelist,
                blacklist=self.error_blacklist,
            ):
                # Apply the whitelist / blacklist logic
                # If it doesn't match, jump over.
                log.debug(
                    "This error type is %s. Skipping for %s #%d",
                    obj["error"],
                    self._transport_type,
                    self.pub_id,
                )
                napalm_logs_publisher_whitelist_blacklist_check_fail.labels(
                    publisher_type=self._transport_type,
                    address=self.address,
                    port=self.port,
                ).inc()
                continue
            serialized_obj = self._serialize(obj, bin_obj)
            log.debug("Publishing the OC object")
            if not self.disable_security and self.__transport_encrypt:
                # Encrypt only when needed.
                serialized_obj = self._prepare(serialized_obj)
            self.transport.publish(serialized_obj)
            napalm_logs_publisher_messages_published.labels(
                publisher_type=self._transport_type,
                address=self.address,
                port=self.port,
            ).inc()

    def stop(self):
        log.info(
            "Stopping publisher process %s (publisher #%d)",
            self._transport_type,
            self.pub_id,
        )
        self.__up = False
        self.sub.close()
        self.ctx.term()
