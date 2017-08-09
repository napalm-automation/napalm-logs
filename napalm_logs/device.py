# -*- coding: utf-8 -*-
'''
Device worker process
'''
from __future__ import absolute_import

# Import python stdlib
import os
import re
import time
import signal
import logging
import threading
from datetime import datetime

# Import thrid party libs
import zmq
import umsgpack

# Import napalm-logs pkgs
import napalm_logs.utils
from napalm_logs.proc import NapalmLogsProc
from napalm_logs.config import PUB_IPC_URL
from napalm_logs.config import DEV_IPC_URL_TPL
from napalm_logs.config import UNKNOWN_DEVICE_NAME
# exceptions
from napalm_logs.exceptions import NapalmLogsExit

log = logging.getLogger(__name__)


class NapalmLogsDeviceProc(NapalmLogsProc):
    '''
    Device sub-process class.
    '''
    def __init__(self, name, config, pipe, pub_pipe, publisher_opts):
        self._name = name
        self.pipe = pipe
        self._config = config
        self.pub_pipe = pub_pipe
        self.publisher_opts = publisher_opts
        self.__up = False
        self.compiled_messages = None
        self._compile_messages()

    def _exit_gracefully(self, signum, _):
        log.debug('Caught signal in %s device process', self._name)
        self.stop()

    def _setup_ipc(self):
        '''
        Subscribe to the right topic
        in the device IPC and publish to the
        publisher proxy.
        '''
        ctx = zmq.Context()
        # subscribe to device IPC
        self.sub = ctx.socket(zmq.PULL)
        # subscribe to the corresponding IPC pipe
        ipc_url = DEV_IPC_URL_TPL.format(os=self._name)
        self.sub.connect(ipc_url)
        # self.sub.setsockopt(zmq.SUBSCRIBE, '')
        # publish to the publisher IPC
        self.pub = ctx.socket(zmq.PUB)
        self.pub.connect(PUB_IPC_URL)

    def _compile_messages(self):
        '''
        Create a list of all OS messages and their compiled regexs
        '''
        self.compiled_messages = []
        if not self._config:
            return
        for message_dict in self._config.get('messages', {}):
            error = message_dict['error']
            tag = message_dict['tag']
            model = message_dict['model']
            match_on = message_dict.get('match_on', 'tag')
            if '__python_fun__' in message_dict:
                self.compiled_messages.append({
                    'error': error,
                    'tag': tag,
                    'match_on': match_on,
                    'model': model,
                    '__python_fun__': message_dict['__python_fun__']
                })
                continue
            values = message_dict['values']
            line = message_dict['line']
            mapping = message_dict['mapping']
            # We will now figure out which position each value is in so we can use it with the match statement
            position = {}
            replace = {}
            for key in values.keys():
                if '|' in key:
                    new_key, replace[new_key] = key.replace(' ', '').split('|')
                    values[new_key] = values.pop(key)
                    key = new_key
                position[line.find('{' + key + '}')] = key
            sorted_position = {}
            for i, elem in enumerate(sorted(position.items())):
                sorted_position[elem[1]] = i + 1
            # Escape the line, then remove the escape for the curly bracets so they can be used when formatting
            escaped = re.escape(line).replace('\{', '{').replace('\}', '}')
            # Replace a whitespace with \s+
            escaped = escaped.replace('\ ', '\s+')
            self.compiled_messages.append(
                {
                    'error': error,
                    'tag': tag,
                    'match_on': match_on,
                    'line': re.compile(escaped.format(**values)),
                    'positions': sorted_position,
                    'values': values,
                    'replace': replace,
                    'model': model,
                    'mapping': mapping
                }
            )

    def _parse(self, msg_dict):
        '''
        Parse a syslog message and check what OpenConfig object should
        be generated.
        '''
        error_present = False
        for message in self.compiled_messages:
            match_on = message['match_on']
            if message[match_on] != msg_dict[match_on]:
                continue
            if '__python_fun__' in message:
                return {
                    'model': message['model'],
                    'error': message['error'],
                    '__python_fun__': message['__python_fun__']
                }
            error_present = True
            match = message['line'].search(msg_dict['message'])
            if not match:
                continue
            positions = message.get('positions', {})
            values = message.get('values')
            ret = {
                'model': message['model'],
                'mapping': message['mapping'],
                'replace': message['replace'],
                'error': message['error']
            }
            for key in values.keys():
                # Check if the value needs to be replaced
                if key in message['replace']:
                    result = napalm_logs.utils.cast(match.group(positions.get(key)), message['replace'][key])
                else:
                    result = match.group(positions.get(key))
                ret[key] = result
            return ret
        if error_present is True:
            log.info('Configured regex did not match for os: %s tag %s', self._name, msg_dict.get('tag', ''))
        else:
            log.info('Syslog message not configured for os: %s tag %s', self._name, msg_dict.get('tag', ''))

    def _emit(self, **kwargs):
        '''
        Emit an OpenConfig object given a certain combination of
        fields mappeed in the config to the corresponding hierarchy.
        '''
        oc_dict = {}
        for mapping, result_key in kwargs['mapping']['variables'].items():
            result = kwargs[result_key]
            oc_dict = napalm_logs.utils.setval(mapping.format(**kwargs), result, oc_dict)
        for mapping, result in kwargs['mapping']['static'].items():
            oc_dict = napalm_logs.utils.setval(mapping.format(**kwargs), result, oc_dict)

        return oc_dict

    def _publish(self, obj):
        '''
        Publish the OC object.
        '''
        bin_obj = umsgpack.packb(obj)
        self.pub.send(bin_obj)

    def _format_time(self, time, date, timezone, prefix_id):
        # TODO can we work out the time format from the regex? Probably but this is a task for another day
        time_format = self._config['prefixes'][prefix_id].get('time_format', '')
        if not time or not date or not time_format:
            return int(datetime.now().strftime('%s'))
        # Most syslog do not include the year, so we will add the current year if we are not supplied with one
        if '%y' in time_format or '%Y' in time_format:
            parsed_time = datetime.strptime('{} {}'.format(date, time), time_format)
        else:
            year = datetime.now().year
            parsed_time = datetime.strptime('{} {} {}'.format(year, date, time), '%Y {}'.format(time_format))
        return int((parsed_time - datetime(1970, 1, 1)).total_seconds())

    def start(self):
        '''
        Start the worker process.
        '''
        # self._setup_ipc()
        # Start suicide polling thread
        thread = threading.Thread(target=self._suicide_when_without_parent, args=(os.getppid(),))
        thread.start()
        signal.signal(signal.SIGTERM, self._exit_gracefully)
        self.__up = True
        while self.__up:
            # bin_obj = self.sub.recv()
            # msg_dict, address = umsgpack.unpackb(bin_obj, use_list=False)
            try:
                msg_dict, address = self.pipe.recv()
            except IOError as error:
                if self.__up is False:
                    return
                else:
                    msg = 'Received IOError on {} device pipe: {}'.format(self._name, error)
                    log.error(msg, exc_info=True)
                    raise NapalmLogsExit(msg)
            log.debug('%s: dequeued %s, received from %s', self._name, msg_dict, address)
            if self._name == UNKNOWN_DEVICE_NAME:
                # If running in the sub-process publishing messages for unknown OSs.
                # This will always send what receives, as-is.
                log.debug('Publishing the message as-is, no further processing possible.')
                to_publish = {
                    'ip': address,
                    'host': 'unknown',
                    'timestamp': int(time.time()),
                    'message_details': msg_dict,
                    'os': UNKNOWN_DEVICE_NAME,
                    'error': 'UNKNOWN',
                    'model_name': 'unknown'
                }
                log.debug('Queueing to be published:')
                log.debug(to_publish)
                self.pub_pipe.send(to_publish)
                continue
            # From here on, we're running in a regular OS sub-process.
            host = msg_dict.get('host')
            prefix_id = msg_dict.pop('__prefix_id__')
            if 'timestamp' in msg_dict:
                timestamp = msg_dict.pop('timestamp')
            else:
                timestamp = self._format_time(msg_dict.get('time', ''),
                                              msg_dict.get('date', ''),
                                              msg_dict.get('timeZone', 'UTC'),
                                              prefix_id)
            facility = msg_dict.get('facility')
            severity = msg_dict.get('severity')

            kwargs = self._parse(msg_dict)
            if not kwargs:
                # Unable to identify what model to generate for the message in cause.
                if self.publisher_opts.get('send_raw'):
                    # But publish the message when the user requested to push raw messages.
                    to_publish = {
                        'ip': address,
                        'host': host,
                        'timestamp': timestamp,
                        'message_details': msg_dict,
                        'os': self._name,
                        'error': 'RAW',
                        'model_name': 'raw',
                        'facility': facility,
                        'severity': severity
                    }
                    log.debug('Queueing to be published:')
                    log.debug(to_publish)
                    self.pub_pipe.send(to_publish)
                continue
            try:
                if '__python_fun__' in kwargs:
                    log.debug('Using the Python parser to determine the YANG-equivalent object')
                    yang_obj = kwargs['__python_fun__'](msg_dict)
                else:
                    yang_obj = self._emit(**kwargs)
            except Exception:
                log.exception('Unexpected error when generating the OC object.', exc_info=True)
                continue
            log.debug('Generated OC object:')
            log.debug(yang_obj)
            error = kwargs.get('error')
            model_name = kwargs.get('model')
            to_publish = {
                'error': error,
                'host': host,
                'ip': address,
                'timestamp': timestamp,
                'yang_message': yang_obj,
                'message_details': msg_dict,
                'yang_model': model_name,
                'os': self._name,
                'facility': facility,
                'severity': severity
            }
            log.debug('Queueing to be published:')
            log.debug(to_publish)
            self.pub_pipe.send(to_publish)
            # self._publish(to_publish)

    def stop(self):
        '''
        Stop the worker process.
        '''
        log.info('Stopping %s device process', self._name)
        self.__up = False
        self.pipe.close()
        self.pub_pipe.close()
