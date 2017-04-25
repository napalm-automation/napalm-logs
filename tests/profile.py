# -*- coding: utf-8 -*-
'''
Profile the napalm-logs processor
'''
from __future__ import absolute_import

# Import python stdlib
from multiprocessing import Process

# Import third party libs
import zmq
import time
import socket

# Import napalm-logs pkgs
import napalm_logs.utils
import napalm_logs.config

CERTIFICATE_PATH = '/tmp/__napalm_logs.crt'
SYSLOG_MSG = ('<149>Mar 30 12:45:19  re0.edge01.bjm01 '
              'rpd[2902]: BGP_PREFIX_THRESH_EXCEEDED: 172.17.17.1 '
              '(External AS 123456): Configured maximum prefix-limit '
              'threshold(160) exceeded for inet-unicast nlri: 181 '
              '(instance master)')
ROUTERS = 10  # count of devices producing syslog messages
PACE = 10000  # messages per second
HEAT_TIME = 10  # 10 seconds to full the buffer
RUN_TIME = 60


def client():
    '''
    Start the client and listen to messages.
    '''
    pk, vk = napalm_logs.utils.authenticate(CERTIFICATE_PATH)
    context = zmq.Context()
    sock = context.socket(zmq.SUB)
    sock.connect('tcp://{addr}:{port}'.format(
        addr=napalm_logs.config.PUBLISH_ADDRESS,
        port=napalm_logs.config.PUBLISH_PORT))
    sock.setsockopt(zmq.SUBSCRIBE, '')
    heat_stop = time.time() + HEAT_TIME
    stop_time = time.time() + RUN_TIME
    while time.time()< heat_stop:
        obj = sock.recv()
        decrypted = napalm_logs.utils.decrypt(obj, vk, pk)
    count = 0
    while time.time() < stop_time:
        obj = sock.recv()
        decrypted = napalm_logs.utils.decrypt(obj, vk, pk)
        count += 1
    print('Received {0} messages in {1} seconds'.format(count, RUN_TIME-HEAT_TIME))


def router():
    '''
    Artificially inject dummy syslog messages
    with a very high rate.
    Multiple instances of this have to be started,
    sending messages to the same
    '''
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    stop_time = time.time() + RUN_TIME
    while time.time() < stop_time:
        skt.sendto(SYSLOG_MSG,
                   (napalm_logs.config.ADDRESS,
                    napalm_logs.config.ADDRESS))
        time.sleep(float(1/PACE))


def main():
    '''
    Start profiling.
    '''
    for _ in range(ROUTERS):
        rproc = Process(target=router)
        rproc.start()
    cproc = Process(target=client)
    cproc.start()


if __name__ == '__main__':
    main()
