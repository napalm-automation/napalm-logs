# -*- coding: utf-8 -*-
'''
Test fixtures for the napalm-logs profiles.
'''
from __future__ import absolute_import

# Import python std lib
import os
import json
import time
import socket
import logging
from multiprocessing import Process

# Import third party lib
import zmq
import pytest

# Import napalm-logs pkgs
import napalm_logs.config
from napalm_logs.base import NapalmLogs

log = logging.getLogger(__name__)

NL_BASE = None
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
    global NL_BASE
    global NL_PROC
    log.debug('Starting up the napalm-logs process')
    NL_BASE = NapalmLogs(disable_security=True,
                         address=NAPALM_LOGS_TEST_ADDR,
                         port=NAPALM_LOGS_TEST_PORT,
                         publish_address=NAPALM_LOGS_TEST_PUB_ADDR,
                         publish_port=NAPALM_LOGS_TEST_PUB_PORT,
                         log_level=NAPALM_LOGS_TEST_LOG_LEVEL)
    NL_PROC = Process(target=NL_BASE.start_engine)
    NL_PROC.start()


# Startup the napalm-logs process
startup_proc()


def startup_local_client():
    '''
    Startup a local ZMQ client to receive the published messages.
    '''
    time.sleep(2)
    global TEST_CLIENT
    context = zmq.Context()
    TEST_CLIENT = context.socket(zmq.SUB)
    TEST_CLIENT.connect('tcp://{addr}:{port}'.format(
        addr=NAPALM_LOGS_TEST_PUB_ADDR,
        port=NAPALM_LOGS_TEST_PUB_PORT)
    )
    TEST_CLIENT.setsockopt(zmq.SUBSCRIBE, b'')


# Startup the local ZMQ client.
startup_local_client()


def generate_tests():
    '''
    Generate the list of tests.
    '''
    expected_os_errors = {}
    for os_name, os_cfg in NL_BASE.config_dict.items():
        expected_os_errors[os_name] = []
        for message in os_cfg['messages']:
            expected_os_errors[os_name].append(message['error'])
    test_cases = []
    cwd = os.path.dirname(__file__)
    test_path = os.path.join(cwd, 'config')
    os_dir_list = [name for name in os.listdir(test_path) if os.path.isdir(os.path.join(test_path, name))]
    expected_oss = set(expected_os_errors.keys())
    tested_oss = set(os_dir_list)
    missing_oss = expected_oss - tested_oss
    for missing_os in missing_oss:
        test_cases.append(('__missing__{}'.format(missing_os), '', ''))
    for os_name in os_dir_list:
        # Subdir is the OS name
        os_path = os.path.join(test_path, os_name)
        errors = [name for name in os.listdir(os_path) if os.path.isdir(os.path.join(os_path, name))]
        expected_errors = set(expected_os_errors[os_name])
        defined_errors = set(errors)
        missing_errors = expected_errors - defined_errors
        for mising_err in missing_errors:
            test_cases.append((os_name, '__missing__{}'.format(mising_err), ''))
        for error_name in errors:
            error_path = os.path.join(os_path, error_name)
            cases = [name for name in os.listdir(error_path) if os.path.isdir(os.path.join(error_path, name))]
            if not cases:
                test_cases.append((os_name, error_name, '__missing__'))
            for test_case in cases:
                test_cases.append((os_name, error_name, test_case))
    return test_cases


# Determine the test cases.
tests = generate_tests()


@pytest.mark.parametrize("os_name,error_name,test_case", tests)
def test_config(os_name, error_name, test_case):
    assert not os_name.startswith('__missing__'), 'No tests defined for {}'.format(os_name.replace('__missing__', ''))
    assert not error_name.startswith('__missing__'),\
        'No tests defined for {}, under {}'.format(error_name.replace('__missing__', ''), os_name)
    assert test_case != '__missing__', 'No test cases defined for {}, under {}'.format(error_name, os_name)
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
    zmq_msg = TEST_CLIENT.recv()
    deserialised_zmq_msg = napalm_logs.utils.unserialize(zmq_msg)
    log.debug('Received from the napalm-logs daemon:')
    log.debug(deserialised_zmq_msg)
    assert struct_yang_message == json.loads(json.dumps(deserialised_zmq_msg))


def test_napalm_logs_shut():
    '''
    Shutdown the napalm-logs engine.
    '''
    NL_BASE.stop_engine()
    assert NL_PROC.is_alive()
    NL_PROC.terminate()
    NL_PROC.join()
