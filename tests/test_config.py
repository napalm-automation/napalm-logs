# -*- coding: utf-8 -*-
'''
Test fixtures for the napalm-logs profiles.
'''
from __future__ import absolute_import

# Import python std lib
import os
import json
import socket
import logging
from multiprocessing import Process

# Import third party lib
import zmq
import pytest
from deepdiff import DeepDiff

# Import napalm-logs pkgs
import napalm_logs.config
from napalm_logs.base import NapalmLogs

log = logging.getLogger(__name__)

NL_PROC = None
TEST_SKT = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
TEST_CLIENT = None

NAPALM_LOGS_TEST_LOG_LEVEL = os.getenv('NAPALM_LOGS_TEST_LOG_LEVEL', default='warning')
NAPALM_LOGS_TEST_ADDR = os.getenv('NAPALM_LOGS_TEST_ADDR', default='0.0.0.0')
NAPALM_LOGS_TEST_PORT = os.getenv('NAPALM_LOGS_TEST_PORT', default=17191)
NAPALM_LOGS_TEST_PUB_ADDR = os.getenv('NAPALM_LOGS_TEST_PUB_ADDR', default='0.0.0.0')
NAPALM_LOGS_TEST_PUB_PORT = os.getenv('NAPALM_LOGS_TEST_PUB_PORT', default=17193)

logging_level = napalm_logs.config.LOGGING_LEVEL.get(NAPALM_LOGS_TEST_LOG_LEVEL.lower())
logging.basicConfig(level=logging_level, format=napalm_logs.config.LOG_FORMAT)


def startup_proc():
    '''
    Startup the napalm-logs process.
    '''
    global NL_PROC
    log.debug('Starting up the napalm-logs process')
    nl_base = NapalmLogs(disable_security=True,
                         address=NAPALM_LOGS_TEST_ADDR,
                         port=NAPALM_LOGS_TEST_PORT,
                         publish_address=NAPALM_LOGS_TEST_PUB_ADDR,
                         publish_port=NAPALM_LOGS_TEST_PUB_PORT,
                         log_level=NAPALM_LOGS_TEST_LOG_LEVEL)
    NL_PROC = Process(target=nl_base.start_engine)
    NL_PROC.start()


# Startup the napalm-logs process
startup_proc()


def startup_local_client():
    '''
    Startup a local ZMQ client to receive the published messages.
    '''
    global TEST_CLIENT
    context = zmq.Context()
    TEST_CLIENT = context.socket(zmq.SUB)
    TEST_CLIENT.connect('tcp://{addr}:{port}'.format(
        addr=NAPALM_LOGS_TEST_PUB_ADDR,
        port=NAPALM_LOGS_TEST_PUB_PORT)
    )
    TEST_CLIENT.setsockopt(zmq.SUBSCRIBE, '')


# Startup the local ZMQ client.
startup_local_client()


def generate_tests():
    '''
    Generate the list of tests.
    '''
    test_cases = []
    cwd = os.path.dirname(__file__)
    test_path = os.path.join(cwd, 'config')
    os_list = [sdpath[0] for sdpath in os.walk(test_path)][1:]
    for os_path in os_list:
        # Subdir is the OS name
        os_name = os.path.split(os_path)[1]
        errors = [sdpath[0] for sdpath in os.walk(os_path)][1:]
        for error_path in errors:
            error_name = os.path.split(error_path)[1]
            cases = [sdpath[0] for sdpath in os.walk(error_path)][1:]
            for test_path in cases:
                test_case = os.path.split(test_path)[1]
                test_cases.append((os_name, error_name, test_case))
    return test_cases


# Determine the test cases.
tests = generate_tests()


@pytest.mark.parametrize("os_name,error_name,test_case", tests)
def test_config(os_name, error_name, test_case):
    print('Testing {} for {}, under the test case "{}"'.format(
          error_name, os_name, test_case))
    cwd = os.path.dirname(__file__)
    test_path = os.path.join(cwd, 'config', os_name, error_name, test_case)
    raw_message_filepath = os.path.join(test_path, 'syslog.msg')
    log.debug('Looking for %s', raw_message_filepath)
    assert os.path.isfile(raw_message_filepath)
    with open(raw_message_filepath, 'r') as raw_message_fh:
        raw_message = raw_message_fh.read()
    log.debug('Read raw message:')
    log.debug(raw_message)
    yang_message_filepath = os.path.join(test_path, 'yang.json')
    log.debug('Looking for %s', yang_message_filepath)
    assert os.path.isfile(yang_message_filepath)
    with open(yang_message_filepath, 'r') as yang_message_fh:
        yang_message = yang_message_fh.read()
    log.debug('Read YANG text:')
    log.debug(yang_message)
    struct_yang_message = json.loads(yang_message)
    log.debug('Struct YANG message:')
    log.debug(struct_yang_message)
    log.debug('Sending the raw message to the napalm-logs daemon')
    TEST_SKT.sendto(raw_message.strip(), (NAPALM_LOGS_TEST_ADDR, NAPALM_LOGS_TEST_PORT))
    log.debug('Waiting fro napalm-logs reply:')
    zmq_msg = TEST_CLIENT.recv()
    deserialised_zmq_msg = napalm_logs.utils.unserialize(zmq_msg)
    log.debug('Received from the napalm-logs daemon:')
    log.debug(deserialised_zmq_msg)
    assert DeepDiff(struct_yang_message, deserialised_zmq_msg)


def test_napalm_logs_shut():
    '''
    Shutdown the napalm-logs engine.
    '''
    assert NL_PROC.is_alive()
    NL_PROC.terminate()
    NL_PROC.join()
