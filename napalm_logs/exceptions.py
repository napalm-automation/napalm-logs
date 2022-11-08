# -*- coding: utf-8 -*-
"""
napalm-logs exceptions.
"""
from __future__ import absolute_import


class NapalmLogsException(Exception):
    """
    Base exception class; all napalm-logs exceptions should inherit this.
    """

    def __init__(self, msg=""):
        super(NapalmLogsException, self).__init__(msg)
        self.strerror = msg


class BindException(NapalmLogsException):
    """
    Exception raised when unable to bind the listener to the specified IP
    address / port. Either the values are not correct, either another processs
    is already using them.
    """

    pass


class TransportException(NapalmLogsException):
    """
    Exception raised when encounering an error in a transport process.
    """

    pass


class InvalidTransportException(TransportException):
    """
    Raised when the user selects a transport that does not exist.
    """

    pass


class ListenerException(NapalmLogsException):
    """
    Exception raised when encountering an exception in a listener process.
    """

    pass


class InvalidListenerException(ListenerException):
    """
    Raised when the user selets a listener that does not exist.
    """

    pass


class SerializerException(NapalmLogsException):
    """
    Raised in case of serializer-related errors.
    """

    pass


class InvalidSerializerException(SerializerException):
    """
    Raised when the user selects a serializer not available.
    """

    pass


class BufferException(NapalmLogsException):
    """
    Raised in case of buffer errors.
    """

    pass


class InvalidBufferException(BufferException):
    """
    Raised when the user selects a buffer interface that is not available.
    """

    pass


class ConfigurationException(NapalmLogsException):
    """
    Exception thrown when the user configuration is not correct.
    """

    pass


class OpenConfigPathException(NapalmLogsException):
    """
    Unable to set the open config path specified.
    """

    pass


class NapalmLogsExit(NapalmLogsException):
    """
    Raised on unexpected exit.
    """

    pass


class CryptoException(NapalmLogsException):
    """
    Raised when unable to decrypt.
    """

    pass


class BadSignatureException(NapalmLogsException):
    """
    Raised when the signature was forged or corrupted.
    """

    pass


class SSLMismatchException(NapalmLogsException):
    """
    Raised when the SSL certificate and key do not match
    """

    pass


class ClientConnectException(NapalmLogsException):
    """
    Raised when the client is unable to connect.
    """

    pass
