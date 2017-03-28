# -*- coding: utf-8 -*-
'''
Server worker process
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import pythond stdlib
import os
import logging
import re
import threading

# Import napalm-logs pkgs
from napalm_logs.proc import NapalmLogsProc

log = logging.getLogger(__name__)


class NapalmLogsServerProc(NapalmLogsProc):
    '''
    Server sub-process class.
    '''
    def __init__(self,
                 pipe,
                 os_pipe_map,
                 config):
        self.config = config
        self.__pipe = pipe
        self.__os_pipe_map = os_pipe_map
        self.__up = False
        self.compiled_prefixes = None
        self._compile_prefixes()

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
        for dev_os, data in self.compiled_prefixes.iteritems():
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

    def start(self):
        '''
        Take the messages from the queue,
        inspect and identify the operating system,
        then queue the message correspondingly.
        '''
        # Start suicide polling thread
        thread = threading.Thread(target=self._suicide_when_without_parent, args=(os.getppid(),))
        thread.start()
        self.__up = True
        while self.__up:
            # Take messages from the main queue
            msg, address = self.__pipe.recv()
            dev_os, msg_dict = self._identify_os(msg)
            if not dev_os or not isinstance(msg_dict, dict):
                # _identify_os shoudl return a string and a dict
                # providing the info for the device OS
                # and the decoded message prefix
                continue
            # Then send the message in the right queue
            self.__os_pipe_map[dev_os].send((msg_dict, address))

    def stop(self):
        self.__up = False
