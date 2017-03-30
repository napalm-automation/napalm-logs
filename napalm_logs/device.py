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

# Import napalm-logs pkgs
from napalm_logs.proc import NapalmLogsProc
from napalm_logs.config import DEFAULT_DELIM

log = logging.getLogger(__name__)


class NapalmLogsDeviceProc(NapalmLogsProc):
    '''
    Device sub-process class.
    '''
    def __init__(self,
                 name,
                 config,
                 transport,
                 pipe):
        self._name = name
        self._config = config
        self._transport = transport
        self._pipe = pipe
        self.__up = False
        self.compiled_messages = None
        self._compile_messages()

    def __del__(self):
        self.stop()
        # Make sure to close the pipe
        self._pipe.close()
        delattr(self, '_pipe')

    def _compile_messages(self):
        '''
        Create a dict of all OS messages and their compiled regexs
        '''
        self.compiled_messages = {}
        if not self._config:
            return
        for message_name, data in self._config.get('messages', {}).items():
            values = data.get('values', {})
            line = data.get('line', '')

            # We will now figure out which position each value is in so we can use it with the match statement
            position = {}
            for key in values.keys():
                position[line.find('{' + key + '}')] = key
            sorted_position = {}
            for i, elem in enumerate(sorted(position.items())):
                sorted_position[elem[1]] = i + 1

            # Escape the line, then remove the escape for the curly bracets so they can be used when formatting
            escaped = re.escape(line).replace('\{', '{').replace('\}', '}')

            self.compiled_messages[message_name] = {
                'line': re.compile(escaped.format(**values)),
                'positions': sorted_position,
                'values': values
                }

    def _parse(self, msg_dict):
        '''
        Parse a syslog message and check what OpenConfig object should
        be generated.
        '''
        regex_data = self.compiled_messages.get(msg_dict['error'])
        if not regex_data:
            log.debug('Unable to find entry for os: {} error {}'.format(self._name, msg_dict.get('error', '')))
            return
        match = regex_data.get('line', '').search(msg_dict['message'])
        if not match:
            log.debug(
                'Configured regex did not match for os: {} error {}'.format(
                    self._name,
                    msg_dict.get('error', '')
                    )
                )
            return
        positions = regex_data.get('positions', {})
        values = regex_data.get('values')
        ret = {}
        for key in values.keys():
            ret[key] = match.group(positions.get(key))
        return ret

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
        pass

    def _publish(self, obj):
        '''
        Publish the OC object.
        '''
        self._transport.publish(obj)

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
            # oc_obj = self._emit(self, **kwargs)
            # self._publish(oc_obj)
            kwargs = self._parse(msg_dict)

    def stop(self):
        '''
        Stop the worker process.
        '''
        self.__up = False
