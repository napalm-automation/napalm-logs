# -*- coding: utf-8 -*-
'''
napalm-logs utilities
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import pythond stdlib
import ssl
import socket
import logging

# Import python stdlib
import umsgpack
import nacl.secret
import nacl.signing
import nacl.encoding
from nacl.exceptions import CryptoError
from nacl.exceptions import BadSignatureError

# Import napalm-logs pkgs
import napalm_logs.config as defaults
from napalm_logs.exceptions import CryptoException
from napalm_logs.exceptions import BadSignatureException

log = logging.getLogger(__name__)


def authenticate(certificate,
                 address=defaults.AUTH_ADDRESS,
                 port=defaults.AUTH_PORT):
    '''
    Authenticate the client and return the private
    and signature keys.

    Establish a connection through a secured socket,
    then do the handshake using the napalm-logs
    auth algorithm.
    '''
    if ':' in address:
        skt_ver = socket.AF_INET6
    else:
        skt_ver = socket.AF_INET
    skt = socket.socket(skt_ver, socket.SOCK_STREAM)
    ssl_skt = ssl.wrap_socket(skt,
                              ca_certs=certificate,
                              cert_reqs=ssl.CERT_REQUIRED)
    ssl_skt.connect((address, port))
    # Explicit INIT
    ssl_skt.write(defaults.MAGIC_REQ)
    # Receive the private key
    private_key = ssl_skt.recv(defaults.BUFFER_SIZE)
    # Send back explicit ACK
    ssl_skt.write(defaults.MAGIC_ACK)
    # Read the hex of the verification key
    verify_key_hex = ssl_skt.recv(defaults.BUFFER_SIZE)
    # Send back explicit ACK
    ssl_skt.write(defaults.MAGIC_ACK)
    # Close the socket
    ssl_skt.close()
    private_key_obj = nacl.secret.SecretBox(private_key)
    verify_key_obj = nacl.signing.VerifyKey(verify_key_hex, encoder=nacl.encoding.HexEncoder)
    return private_key_obj, verify_key_obj


def decrypt(binary, verify_key_obj, private_key_obj):
    '''
    Decrypt and unpack the original OpenConfig object,
    serialized using MessagePack.
    Raise BadSignatureException when the signature
    was forged or corrupted.
    '''
    try:
        encrypted = verify_key_obj.verify(binary)
    except BadSignatureError as bserr:
        log.error('Signature was forged or corrupt', exc_info=True)
        raise BadSignatureException('Signature was forged or corrupt')
    try:
        packed = private_key_obj.decrypt(encrypted)
    except CryptoError as cerr:
        log.error('Unable to decrypt', exc_info=True)
        raise CryptoException('Unable to decrypt')
    return umsgpack.unpackb(packed)

def unserialize(binary):
    '''
    Unpack the original OpenConfig object,
    serialized using MessagePack.
    This is to be used when disable_security is set.
    '''
    return umsgpack.unpackb(binary)
