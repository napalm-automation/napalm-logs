# -*- coding: utf-8 -*-
"""
Authenticator worker process
"""
from __future__ import absolute_import
from __future__ import unicode_literals

# Import pythond stdlib
import os
import ssl
import signal
import socket
import logging
import threading

# Import napalm-logs pkgs
from napalm_logs.config import AUTH_ADDRESS
from napalm_logs.config import AUTH_PORT
from napalm_logs.config import MAGIC_REQ
from napalm_logs.config import MAGIC_ACK
from napalm_logs.proc import NapalmLogsProc
from napalm_logs.config import AUTH_MAX_CONN
from napalm_logs.config import AUTH_KEEP_ALIVE
from napalm_logs.config import AUTH_KEEP_ALIVE_ACK
from napalm_logs.exceptions import BindException
from napalm_logs.exceptions import SSLMismatchException

# exceptions
from napalm_logs.exceptions import NapalmLogsExit

log = logging.getLogger(__name__)


class NapalmLogsAuthProc(NapalmLogsProc):
    """
    Authenticator sub-process class.
    This process waits for the clients to request
    the private and signing keys.
    The communication should be established through SSL
    sockets only, the identify being verificated
    using the TLS certificate.

    Algorithm:

    Log server                    Log consumer
    -------------------------------------------
        |                               |
        | <----------- INIT ----------- |
        |                               |
        | ------- send PRV key -------> |
        |                               |
        | <------------ ACK ----------- |
        |                               |
        | ------- send SGN HEX -------> |
        |                               |
        | <------------ ACK ----------- |
    """

    def __init__(
        self,
        certificate,
        keyfile,
        private_key,
        signature_hex,
        auth_address=AUTH_ADDRESS,
        auth_port=AUTH_PORT,
    ):
        self.certificate = certificate
        self.keyfile = keyfile
        self.__key = private_key
        self.__sgn = signature_hex
        self.auth_address = auth_address
        self.auth_port = auth_port
        self.__up = False
        self.socket = None

    def _exit_gracefully(self, signum, _):  # pylint: disable=unused-argument
        """
        Exit gracefully.
        """
        self.stop()

    def _handshake(self, conn, addr):
        """
        Ensures that the client receives the AES key.
        """
        # waiting for the magic request message
        msg = conn.recv(len(MAGIC_REQ))
        log.debug("Received message %s from %s", msg, addr)
        if msg != MAGIC_REQ:
            log.warning("%s is not a valid REQ message from %s", msg, addr)
            return
        log.debug("Sending the private key")
        conn.send(self.__key)
        # wait for explicit ACK
        log.debug("Waiting for the client to confirm")
        msg = conn.recv(len(MAGIC_ACK))
        if msg != MAGIC_ACK:
            return
        log.debug("Sending the signature key")
        conn.send(self.__sgn)
        # wait for explicit ACK
        log.debug("Waiting for the client to confirm")
        msg = conn.recv(len(MAGIC_ACK))
        if msg != MAGIC_ACK:
            return
        log.info("%s is now authenticated", addr)
        self.keep_alive(conn)

    def keep_alive(self, conn):
        """
        Maintains auth sessions
        """
        while self.__up:
            msg = conn.recv(len(AUTH_KEEP_ALIVE))
            if msg != AUTH_KEEP_ALIVE:
                log.error("Received something other than %s", AUTH_KEEP_ALIVE)
                conn.close()
                return
            try:
                conn.send(AUTH_KEEP_ALIVE_ACK)
            except (IOError, socket.error) as err:
                log.error("Unable to send auth keep alive: %s", err)
                conn.close()
                return

    def verify_cert(self):
        """
        Checks that the provided cert and key are valid and usable
        """
        log.debug(
            "Verifying the %s certificate, keyfile: %s", self.certificate, self.keyfile
        )
        try:
            ssl.create_default_context().load_cert_chain(
                self.certificate, keyfile=self.keyfile
            )
        except ssl.SSLError:
            error_string = "SSL certificate and key do not match"
            log.error(error_string)
            raise SSLMismatchException(error_string)
        except IOError:
            log.error("Unable to open either certificate or key file")
            raise
        log.debug("Certificate looks good.")

    def _create_skt(self):
        """
        Create the authentication socket.
        """
        log.debug("Creating the auth socket")
        if ":" in self.auth_address:
            self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.bind((self.auth_address, self.auth_port))
        except socket.error as msg:
            error_string = "Unable to bind (auth) to port {} on {}: {}".format(
                self.auth_port, self.auth_address, msg
            )
            log.error(error_string, exc_info=True)
            raise BindException(error_string)

    def start(self):
        """
        Listen to auth requests and send the AES key.
        Each client connection starts a new thread.
        """
        # Start suicide polling thread
        log.debug("Starting the auth process")
        self.verify_cert()
        self._create_skt()
        log.debug(
            "The auth process can receive at most %d parallel connections",
            AUTH_MAX_CONN,
        )
        self.socket.listen(AUTH_MAX_CONN)
        thread = threading.Thread(
            target=self._suicide_when_without_parent, args=(os.getppid(),)
        )
        thread.start()
        signal.signal(signal.SIGTERM, self._exit_gracefully)
        self.__up = True
        while self.__up:
            try:
                (clientsocket, address) = self.socket.accept()
                wrapped_auth_skt = ssl.wrap_socket(
                    clientsocket,
                    server_side=True,
                    certfile=self.certificate,
                    keyfile=self.keyfile,
                )
            except ssl.SSLError:
                log.exception("SSL error", exc_info=True)
                continue
            except socket.error as error:
                if self.__up is False:
                    return
                else:
                    msg = "Received auth socket error: {}".format(error)
                    log.error(msg, exc_info=True)
                    raise NapalmLogsExit(msg)
            log.info("%s connected", address)
            log.debug("Starting the handshake")
            client_thread = threading.Thread(
                target=self._handshake, args=(wrapped_auth_skt, address)
            )
            client_thread.start()

    def stop(self):
        """
        Stop the auth proc.
        """
        log.info("Stopping auth process")
        self.__up = False
        self.socket.close()
