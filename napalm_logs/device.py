# -*- coding: utf-8 -*-
'''
Device worker process
'''
from __future__ import absolute_import

# Import python stdlib
import os
import re
import signal
import logging
import threading
from datetime import datetime

# Import thrid party libs
import zmq
import umsgpack
import napalm_yang

# Import napalm-logs pkgs
from napalm_logs.proc import NapalmLogsProc
from napalm_logs.config import PUB_IPC_URL
from napalm_logs.config import DEV_IPC_URL_TPL
from napalm_logs.config import DEFAULT_DELIM
from napalm_logs.config import REPLACEMENTS
from napalm_logs.exceptions import OpenConfigPathException
from napalm_logs.exceptions import UnknownOpenConfigModel
# exceptions
from napalm_logs.exceptions import NapalmLogsExit

log = logging.getLogger(__name__)


class NapalmLogsDeviceProc(NapalmLogsProc):
    '''
    Device sub-process class.
    '''
    def __init__(self, name, config, pipe, pub_pipe):
        self._name = name
        self.pipe = pipe
        self._config = config
        self.pub_pipe = pub_pipe
        self.__up = False
        self.compiled_messages = None
        self._compile_messages()
        self.__yang_cache = {}

    def _exit_gracefully(self, signum, _):
        log.debug('Caught signal in {} device process'.format(self._name))
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
            values = message_dict['values']
            replace = message_dict['replace']
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
            # Replace a whitespace with \s+
            escaped = escaped.replace('\ ', '\s+')
            self.compiled_messages.append(
                {
                    'error': error,
                    'tag': tag,
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
            if message['tag'] != msg_dict['tag']:
                continue
            error_present = True
            match = message['line'].search(msg_dict['message'])
            if not match:
                continue
            positions = message.get('positions', {})
            values = message.get('values')
            ret = {
                'oc_model': message['model'],
                'oc_mapping': message['mapping'],
                'replace': message['replace'],
                'error': message['error']
            }
            for key in values.keys():
                # Check if the value needs to be replaced
                if message['replace'].get(key):
                    fun = REPLACEMENTS.get(message['replace'].get(key))
                    result = fun(match.group(positions.get(key)))
                else:
                    result = match.group(positions.get(key))
                ret[key] = result
            return ret
        if error_present is True:
            log.info(
                'Configured regex did not match for os: {} tag {}'.format(
                    self._name,
                    msg_dict.get('tag', '')
                )
            )
        else:
            log.info(
                'Syslog message not configured for os: {} tag {}'.format(
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

    def _get_oc_obj(self, model_name):
        '''
        Return the processed YANG model binded to python object.
        To reduce the overhead, caches the object in memory when
        generation is successful.
        '''
        if model_name in self.__yang_cache:
            return self.__yang_cache[model_name]
        log.debug('YANG binding not cached yet, generating')
        oc_obj = napalm_yang.base.Root()
        try:
            oc_obj.add_model(getattr(napalm_yang.models, model_name))
        except AttributeError:
            error_string = 'Unable to load openconfig module {0},' \
                           ' please make sure the config is correct'.format(model_name)
            log.error(error_string, exc_info=True)
            raise UnknownOpenConfigModel(error_string)
        self.__yang_cache[model_name] = oc_obj
        return oc_obj

    def _emit(self, **kwargs):
        '''
        Emit an OpenConfig object given a certain combination of
        fields mappeed in the config to the corresponding hierarchy.
        '''
        # Load the appropriate OC model
        log.debug('Getting the YANG model binding')
        oc_obj = self._get_oc_obj(kwargs['oc_model'])
        log.debug('Filling the OC model')
        oc_dict = {}
        for mapping, result_key in kwargs['oc_mapping']['variables'].items():
            result = kwargs[result_key]
            oc_dict = self._setval(mapping.format(**kwargs), result, oc_dict)
        for mapping, result in kwargs['oc_mapping']['static'].items():
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
        bin_obj = umsgpack.packb(obj)
        self.pub.send(bin_obj)

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
            log.debug('{0}: dequeued {1}, received from {2}'.format(self._name, msg_dict, address))
            kwargs = self._parse(msg_dict)
            if not kwargs:
                continue
            try:
                oc_obj = self._emit(**kwargs)
            except Exception as err:
                log.exception('Unexpected error when generating the OC object.', exc_info=True)
                continue
            log.debug('Generated OC object:')
            log.debug(oc_obj)
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
            log.debug('Queueing to be published:')
            log.debug(to_publish)
            self.pub_pipe.send(to_publish)
            # self._publish(to_publish)

    def stop(self):
        '''
        Stop the worker process.
        '''
        log.info('Stopping {} device process'.format(self._name))
        self.__up = False
        self.pipe.close()
        self.pub_pipe.close()
