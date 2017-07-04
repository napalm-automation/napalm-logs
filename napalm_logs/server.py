# -*- coding: utf-8 -*-
'''
Server worker process
'''
from __future__ import absolute_import

# Import pythond stdlib
import os
import re
import json
import time
import signal
import logging
import threading

# Import third party libs
import zmq
import umsgpack

# Import napalm-logs pkgs
from napalm_logs.config import LST_IPC_URL
from napalm_logs.config import DEV_IPC_URL_TPL
from napalm_logs.proc import NapalmLogsProc
from napalm_logs.transport import get_transport
# exceptions
from napalm_logs.exceptions import NapalmLogsExit

log = logging.getLogger(__name__)


class NapalmLogsServerProc(NapalmLogsProc):
    '''
    Server sub-process class.
    '''
    def __init__(self, config, pipe, os_pipes, logger):
        self.config = config
        self.pipe = pipe
        self.os_pipes = os_pipes
        self.logger = logger
        self.__up = False
        # self.pubs = {}
        self.compiled_prefixes = None
        self._compile_prefixes()

    def _exit_gracefully(self, signum, _):
        log.debug('Caught signal in server process')
        self.stop()

    def _setup_ipc(self):
        '''
        Setup the IPC pub and sub.
        Subscript to the listener IPC
        and publish to the device specific IPC.
        '''
        ctx = zmq.Context()
        # subscribe to listener
        self.sub = ctx.socket(zmq.PULL)
        self.sub.connect(LST_IPC_URL)
        # device publishers
        os_types = self.config.keys()
        for dev_os in os_types:
            pub = ctx.socket(zmq.PUSH)
            ipc_url = DEV_IPC_URL_TPL.format(os=dev_os)
            pub.bind(ipc_url)
            self.pubs[dev_os] = pub

    def _compile_prefixes(self):
        '''
        Create a dict of all OS prefixes and their compiled regexs
        '''
        self.compiled_prefixes = {}
        for dev_os, os_config in self.config.items():
            if not os_config:
                continue
            values = os_config.get('prefix', {}).get('values', {})
            line = os_config.get('prefix', {}).get('line', '')
            # Add 'pri' and 'message' to the line, and values
            line = '{{pri}}{}{{message}}'.format(line)
            # PRI https://tools.ietf.org/html/rfc5424#section-6.2.1
            values['pri'] = '\<(\d+)\>'
            values['message'] = '(.*)'
            # We will now figure out which position each value is in so we can use it with the match statement
            position = {}
            for key in values.keys():
                position[line.find('{' + key + '}')] = key
            sorted_position = {}
            for i, elem in enumerate(sorted(position.items())):
                sorted_position[elem[1]] = i + 1
            # Escape the line, then remove the escape for the curly bracets so they can be used when formatting
            escaped = re.escape(line).replace('\{', '{').replace('\}', '}')
            # Replace a whitespace with \s+
            escaped = escaped.replace('\ ', '\s+')
            self.compiled_prefixes[dev_os] = {
                'prefix': re.compile(escaped.format(**values)),
                'prefix_positions': sorted_position,
                'values': values
            }

    def _identify_os(self, msg):
        '''
        Using the prefix of the syslog message,
        we are able to identify the operating system and then continue parsing.
        '''
        ret = {}
        for dev_os, data in self.compiled_prefixes.items():
            match = data.get('prefix', '').search(msg)
            if not match:
                continue
            positions = data.get('prefix_positions', {})
            values = data.get('values')
            ret = {}
            for key in values.keys():
                ret[key] = match.group(positions.get(key))
            # TODO Should we stop searching and just return, or should we return all matches OS?
            return dev_os, ret
        log.debug('No OS matched for: {}'.format(msg))
        return '', ret

    def _setup_log_syslog_transport(self):
        transport_class = get_transport(self.logger['syslog'])
        # The tranport classes expect address and port to be passed as args,
        # but as the options for logger are configured via the config file
        # these will be found in **kwargs. So we will send None for both
        address = self.logger.pop('address', None)
        port = self.logger.pop('port', None)
        self._log_syslog_transport = transport_class(address, port, **self.logger)
        self._log_syslog_transport.start()

    def _send_log_syslog(self, dev_os, msg_dict):
        log_dict = {}
        log_dict.update(msg_dict)
        log_dict['os'] = dev_os
        self._log_syslog_transport.publish(json.dumps(log_dict))

    def start(self):
        '''
        Take the messages from the queue,
        inspect and identify the operating system,
        then queue the message correspondingly.
        '''
        # self._setup_ipc()
        # Start suicide polling thread
        thread = threading.Thread(target=self._suicide_when_without_parent, args=(os.getppid(),))
        thread.start()
        signal.signal(signal.SIGTERM, self._exit_gracefully)
        # If were are to log all processed syslogs we need to initiate the class
        if self.logger.get('syslog'):
            self._setup_log_syslog_transport()
        self.__up = True
        while self.__up:
            # Take messages from the main queue
            # bin_obj = self.sub.recv()
            # msg, address = umsgpack.unpackb(bin_obj, use_list=False)
            try:
                msg, address = self.pipe.recv()
            except IOError as error:
                if self.__up is False:
                    return
                else:
                    msg = 'Received IOError from server pipe: {}'.format(error)
                    log.error(msg, exc_info=True)
                    raise NapalmLogsExit(msg)
            log.debug('[{2}] Dequeued message from {0}: {1}'.format(address, msg, time.time()))
            dev_os, msg_dict = self._identify_os(msg)
            log.debug('Identified OS: {0}'.format(dev_os))
            if self.logger.get('syslog'):
                if dev_os:
                    self._send_log_syslog(dev_os, msg_dict)
                else:
                    self._send_log_syslog('unknown', {'message': msg})
            if not dev_os or not isinstance(msg_dict, dict):
                # _identify_os should return a string and a dict
                # providing the info for the device OS
                # and the decoded message prefix
                continue
            # Then send the message in the right queue
            # obj = (msg_dict, address)
            # bin_obj = umsgpack.packb(obj)
            log.debug('Queueing message to {0}'.format(dev_os))
            # self.pubs[dev_os].send(bin_obj)
            self.os_pipes[dev_os].send((msg_dict, address))

    def stop(self):
        log.info('Stopping server process')
        self.__up = False
        self.pipe.close()
        for os_pipe in self.os_pipes.values():
            os_pipe.close()
        if self.logger.get('syslog'):
            self._log_syslog_transport.stop()
