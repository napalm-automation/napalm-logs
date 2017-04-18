# -*- coding: utf-8 -*-
'''
Device worker process
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import python stdlib
import os
import re
import logging
import threading
from datetime import datetime

# Import thrid party libs
import napalm_yang

# Import napalm-logs pkgs
from napalm_logs.proc import NapalmLogsProc
from napalm_logs.config import DEFAULT_DELIM
from napalm_logs.exceptions import OpenConfigPathException
from napalm_logs.exceptions import UnknownOpenConfigModel

log = logging.getLogger(__name__)


class NapalmLogsDeviceProc(NapalmLogsProc):
    '''
    Device sub-process class.
    '''
    def __init__(self,
                 name,
                 config,
                 pipe,
                 transport_pipe):
        self._name = name
        self._config = config
        self._pipe = pipe
        self.__up = False
        self.compiled_messages = None
        self._compile_messages()
        self._transport_pipe = transport_pipe

    def __del__(self):
        self.stop()
        # Make sure to close the pipe
        self._pipe.close()
        delattr(self, '_pipe')

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
            values = message_dict['values']
            line = message_dict['line']
            model = message_dict['model']
            mapping = message_dict['mapping']

            # We will now figure out which position each value is in so we can use it with the match statement
            position = {}
            for key in values.keys():
                position[line.find('{' + key + '}')] = key
            sorted_position = {}
            for i, elem in enumerate(sorted(position.items())):
                sorted_position[elem[1]] = i + 1

            # Escape the line, then remove the escape for the curly bracets so they can be used when formatting
            escaped = re.escape(line).replace('\{', '{').replace('\}', '}')

            self.compiled_messages.append(
                {
                    'error': error,
                    'tag': tag,
                    'line': re.compile(escaped.format(**values)),
                    'positions': sorted_position,
                    'values': values,
                    'model': model,
                    'mapping': mapping
                    }
                )

    def _parse(self, msg_dict):
        '''
        Parse a syslog message and check what OpenConfig object should
        be generated.
        '''
        for message in self.compiled_messages:
            if message['tag'] != msg_dict['tag']:
                continue
            match = message['line'].search(msg_dict['message'])
            if not match:
                continue
            positions = message.get('positions', {})
            values = message.get('values')
            ret = {
                'oc_model': message['model'],
                'oc_mapping': message['mapping'],
                'error': message['error']
                }
            for key in values.keys():
                ret[key] = match.group(positions.get(key))
            return ret
        log.debug(
            'Configured regex did not match for os: {} tag {}'.format(
                self._name,
                msg_dict.get('tag', '')
                )
            )

    @staticmethod
    def _setval(key, val, dict_=None):
        '''
        Set a value under the dictionary hierarchy identified
        under the key. The target 'foo/bar/baz' returns the
        dictionary hierarchy {'foo': {'bar': {'baz': {}}}}.

        .. note::

            Currently this doesn't work with integers, i.e.
            cannot build lists dynamically.
            TODO
        '''
        if not dict_:
            dict_ = {}
        prev_hier = dict_
        dict_hier = key.split(DEFAULT_DELIM)
        for each in dict_hier[:-1]:
            try:
                idx = int(each)
            except ValueError:
                # not int
                if each not in prev_hier:
                    prev_hier[each] = {}
                prev_hier = prev_hier[each]
            else:
                prev_hier[each] = [{}]
                prev_hier = prev_hier[each]
        prev_hier[dict_hier[-1]] = val
        return dict_

    @staticmethod
    def _traverse(data, key):
        '''
        Traverse a dict or list using a slash delimiter target string.
        The target 'foo/bar/0' will return data['foo']['bar'][0] if
        this value exists, otherwise will return empty dict.
        Return None when not found.
        This can be used to verify if a certain key exists under
        dictionary hierarchy.
        '''
        for each in key.split(DEFAULT_DELIM):
            if isinstance(data, list):
                try:
                    idx = int(each)
                except ValueError:
                    embed_match = False
                    # Index was not numeric, lets look at any embedded dicts
                    for embedded in (x for x in data if isinstance(x, dict)):
                        try:
                            data = embedded[each]
                            embed_match = True
                            break
                        except KeyError:
                            pass
                    if not embed_match:
                        # No embedded dicts matched
                        return None
                else:
                    try:
                        data = data[idx]
                    except IndexError:
                        return None
            else:
                try:
                    data = data[each]
                except (KeyError, TypeError):
                    return None
        return data

    def _emit(self, **kwargs):
        '''
        Emit an OpenConfig object given a certain combination of
        fields mappeed in the config to the corresponding hierarchy.
        '''
        # Load the appropriate OC model
        oc_obj = napalm_yang.base.Root()
        try:
            oc_obj.add_model(getattr(napalm_yang.models, kwargs['oc_model']))
        except AttributeError:
            error_string = 'Unable to load openconfig module {0},' \
                           ' please make sure the config is correct'.format(kwargs['oc_model'])
            log.error(error_string, exc_info=True)
            raise UnknownOpenConfigModel(error_string)

        oc_dict = {}
        for result_key, mapping in kwargs['oc_mapping'].items():
            result = kwargs[result_key]
            oc_dict = self._setval(mapping.format(**kwargs), result, oc_dict)
        try:
            oc_obj.load_dict(oc_dict)
        except AttributeError:
            error_string = 'Error whilst mapping to open config, ' \
                           'please check that the mappings are correct for {0}'.format(self._name)
            log.error(error_string, exc_info=True)
            raise OpenConfigPathException(error_string)

        return oc_obj.to_dict(filter=True)

    def _publish(self, obj):
        '''
        Publish the OC object.
        '''
        self._transport_pipe.send(obj)

    def _format_time(self, time, date):
        # TODO can we work out the time format from the regex? Probably but this is a task for another day
        time_format = self._config['prefix'].get('time_format', '')
        if not time or not date or not time_format:
            return datetime.now().strftime('%s')
        # Most syslog do not include the year, so we will add the current year if we are not supplied with one
        if '%y' in date or '%Y' in date:
            timestamp = datetime.strptime('{} {}'.format(date, time), time_format)
        else:
            year = datetime.now().year
            timestamp = datetime.strptime('{} {} {}'.format(year, date, time), '%Y {}'.format(time_format))
        return timestamp.strftime('%s')

    def start(self):
        '''
        Start the worker process.
        '''
        # Start suicide polling thread
        thread = threading.Thread(target=self._suicide_when_without_parent, args=(os.getppid(),))
        thread.start()
        self.__up = True
        while self.__up:
            msg_dict, address = self._pipe.recv()
            # # Will wait till a message is available
            kwargs = self._parse(msg_dict)
            if not kwargs:
                continue
            oc_obj = self._emit(**kwargs)
            error = kwargs.get('error')
            model_name = kwargs.get('oc_model')
            host = msg_dict.get('host')
            timestamp = self._format_time(msg_dict.get('time', ''), msg_dict.get('date', ''))
            to_publish = {
                'error': error,
                'host': host,
                'ip': address,
                'timestamp': timestamp,
                'open_config': oc_obj,
                'message_details': msg_dict,
                'model_name': model_name,
                'os': self._name
            }
            self._publish(to_publish)

    def stop(self):
        '''
        Stop the worker process.
        '''
        self.__up = False
