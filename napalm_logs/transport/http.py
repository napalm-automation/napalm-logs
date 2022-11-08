# -*- coding: utf-8 -*-
"""
HTTP(s) transport for napalm-logs.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

# Import stdlib
import logging
import threading
import json

try:
    import Queue as queue
except ImportError:
    import queue

# Import third party libs
try:
    import requests

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import tornado
    import tornado.httpclient

    HAS_TORNADO = True
except ImportError:
    HAS_TORNADO = False

# Import napalm-logs pkgs
import napalm_logs.utils
from napalm_logs.exceptions import TransportException
from napalm_logs.transport.base import TransportBase

log = logging.getLogger(__name__)


class HTTPTransport(TransportBase):
    """
    HTTP transport class.
    """

    NO_ENCRYPT = True
    # This tells the publisher to not encrypt the messages
    #   published over this channel.

    def __init__(self, address, port, **kwargs):
        if kwargs.get("address"):
            self.address = kwargs["address"]
        else:
            self.address = address
        self.method = kwargs.get("method", "POST")
        log.debug("Publishing to %s using method %s", self.address, self.method)
        self.auth = kwargs.get("auth")
        self.username = kwargs.get("username")
        self.password = kwargs.get("password")
        if not self.auth:
            if self.username and self.password:
                self.auth = (self.username, self.password)
        self.headers = kwargs.get("headers", {})
        self.verify_ssl = kwargs.get("verify_ssl", True)
        self.params = kwargs.get("params")
        self.max_clients = kwargs.get("max_clients", 10)
        self.backend = kwargs.get("backend")
        if not self.backend:
            log.info("No explicit backend requested")
            if HAS_TORNADO:
                self.backend = "tornado"
                log.info("Tornado seems to be installed, so will use")
            elif HAS_REQUESTS:
                self.backend = "requests"
                log.info("Requests seems to be installed, so will use")

    def start(self):
        # Throw errors if backend it not properly configured
        if self.backend not in ("requests", "tornado"):
            raise TransportException("Invalid HTTP backend: %s", self.backend)
        if self.backend == "requests" and not HAS_REQUESTS:
            raise TransportException(
                "Trying to use Requests as backend, but it is not installed"
            )
        if self.backend == "tornado" and not HAS_TORNADO:
            raise TransportException(
                "Trying to use Tornado as backend, but it is not installed"
            )
        # Prepare the tornado backend
        if self.backend == "tornado":
            self.tornado_client = tornado.httpclient.AsyncHTTPClient(
                max_clients=self.max_clients
            )
        elif self.backend == "requests":
            # When using requests, we start a threaded pool
            #   with the size specified using max_clients.
            # Tornado already has this feature built-in.
            # We could just start a single thread per request,
            #   but this leads to infinite number of threads started withing
            #   the Publiser processes. Python is really really bad to collect
            #   the garbage from continuous processes, and this can lead
            #   to memory leaks.
            # So we'll queue the messages to be publishe
            self._publish_queue = queue.Queue()  # TODO: use opts hwm
            self._pool = []
            for index in range(self.max_clients):
                thread = threading.Thread(target=self._publish_requests)
                thread.daemon = True
                thread.start()
                self._pool.append(thread)

    def publish(self, obj):
        data = napalm_logs.utils.unserialize(obj)
        if self.backend == "tornado":
            self.tornado_client.fetch(
                self.address,
                callback=self._handle_tornado_response,
                method=self.method,
                headers=self.headers,
                auth_username=self.username,
                auth_password=self.password,
                body=str(data),
                validate_cert=self.verify_ssl,
                allow_nonstandard_methods=True,
                decompress_response=False,
            )
        elif self.backend == "requests":
            # Queue the publish object async
            self._publish_queue.put_nowait(data)

    def _publish_requests(self):
        while True:
            # 1s timeout so that if the parent dies this thread will die within 1s
            try:
                try:
                    data = self._publish_queue.get(timeout=1)
                    self._publish_queue.task_done()  # Mark the task as done once we get it
                except queue.Empty:
                    # If empty, try again
                    continue
            except AttributeError:
                # During shutdown, `queue` may not have an `Empty` atttribute
                continue
            session = requests.Session()
            session.auth = self.auth
            session.headers.update(self.headers)
            session.verify = self.verify_ssl
            try:
                result = session.request(
                    self.method, self.address, params=self.params, data=json.dumps(data)
                )
                if not result.ok:
                    log.error("Unable to publish to %s", self.address)
                    log.error("Status code: %d", result.status_code)
                    log.error(result.text)
                else:
                    log.debug(result.text)
                del result
            except requests.ConnectionError as conn_err:
                log.error(conn_err)
            del session

    def _handle_tornado_response(self, response):
        if response.error:
            log.error("Unable to publish to %s", self.address)
            log.error(response.error)
        else:
            log.debug(response.body)

    def stop(self):
        if self.backend == "tornado":
            self.tornado_client.close()
        elif self.backend == "requests":
            for thread in self._pool:
                thread.join()
