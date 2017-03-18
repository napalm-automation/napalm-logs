# -*- coding: utf-8 -*-
'''
napalm-logs base
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import std lib
import os
import yaml
import time
import logging

# Import napalm-logs pkgs
import napalm_logs.exceptions
from napalm_logs.proc import NapalmLogsProc
from napalm_logs.transport import get_transport

log = logging.getLogger(__name__)


class NapalmLogs:
    def __init__(self,
                 hostname='0.0.0.0',
                 port=514,
                 transport='zmq',
                 publish_hostname='0.0.0.0',
                 publish_port=49017,
                 config_path=None,
                 config_dict=None,
                 extension_config_path=None,
                 extension_config_dict=None):
        '''
        Init the napalm-logs engine.

        :param hostname: The address to bind the syslog client. Default: 0.0.0.0.
        :param port: Listen port. Default: 514.
        :param publish_hostname: The address to bing when publishing the OC
                                 objects. Default: 0.0.0.0.
        :param publish_port: Publish port. Default: 49017.
        '''
        self.hostname = hostname
        self.port = port
        self.publish_hostname = publish_hostname
        self.publish_port = publish_port
        self.config_path = config_path
        self.config_dict = config_dict
        self.extension_config_path = extension_config_path
        self.extension_config_dict = extension_config_dict
        transport_class = get_transport(transport)
        self.transport = transport_class(self.publish_hostname,
                                         self.publish_port)
        self._build_config()
        self._precompile_regex()
        self.device_proc = {}
        self.__up = False  # Require explicit `start_engine`

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stop_engine()
        if exc_type is not None:
            self.__raise_clean_exception(exc_type, exc_value, exc_traceback)

    def __del__(self):
        self.stop_engine()

    def _load_config(self, path):
        '''
        Read the configuration under a specific path
        and return the object.
        '''
        config = {}
        if not os.path.isdir(path):
            msg = (
                'Unable to read from {path}: '
                'the directory does not exist!'
            ).format(path=path)
            log.error(msg)
            raise IOError(msg)
        files = os.listdir(path)
        # Read all files under the config dir
        for file in files:
            # And allow only .yml and .yaml extensions
            if not file.endswith('.yml') and not file.endswith('.yaml'):
                continue
            filename, _ = file.split('.')
            # The filename is also the network OS name
            filepath = os.path.join(path, file)
            try:
                with open(filepath, 'r') as fstream:
                    config[filename] = yaml.load(fstream)
            except yaml.YAMLError as yamlexc:
                log.error('Invalid YAML file: {}'.format(filepath))
                log.error(yamlexc)
                raise IOError(yamlexc)
        if not config:
            msg = 'Unable to find proper configuration files under {path}'.format(path=path)
            log.error(msg)
            raise IOError(msg)
        return config

    def _build_config(self):
        '''
        Build the config of the napalm syslog parser.
        '''
        if not self.config_dict:
            if not self.config_path:
                # No custom config path requested
                # Read the native config files
                self.config_path = os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    'config'
                )
            log.info('Reading the configuration from {path}'.format(path=self.config_path))
            self.config_dict = self._load_config(self.config_path)
        if not self.extension_config_dict and self.extension_config_path:
            # When extension config is not sent as dict
            # But `extension_config_path` is specified
            log.info('Reading extension configuration from {path}'.format(path=self.extension_config_path))
            self.extension_config_dict = self._load_config(self.extension_config_path)
        elif not self.extension_config_dict:
            self.extension_config_dict = {}
        if not self.extension_config_dict:
            # No extension config, no extra build
            return
        for nos, nos_config in self.extension_config_dict.items():
            if nos not in self.config_dict and nos_config:
                self.config_dict[nos] = nos_config
                continue
            self.config_dict[nos].update(nos_config)

    def _precompile_regex(self):
        '''
        Go through the configuration and precompile all regular expressions,
        so the parsing should be faster.
        '''
        pass

    def _identify_os(self, msg):
        '''
        Using the prefix of the syslog message,
        we are able to identify the operating system and then continue parsing.
        '''
        pass

    def _listen(self):
        '''
        Listen to messages and send them to be served by the right process.
        '''
        self.__up = True
        try:
            while self.__up:
                # TODO: identify the OS and send the message to the right child process
                self.transport.publish('Test')
        except KeyboardInterrupt:
            # Greceful exit.
            log.info('Exiting on Ctrl-C')
            self.stop_engine()

    def start_engine(self):
        '''
        Start the child processes (one per device OS),
        open the socket to start receiving messages.
        '''
        log.info('Preparing the transport')
        self.transport.start()
        log.info('Starting child processes for each device type')
        for device_os, device_config in self.config_dict.items():
            dpid = os.fork()
            if dpid == 0:
                log.info('Starting the child process for {dos}'.format(dos=device_os))
                dos = NapalmLogsProc(device_os,
                                     device_config,
                                     self.transport)
                dos.start()
                os._exit(0)
        log.info('Start listening to syslog messages')
        self._listen()

    def stop_engine(self):
        log.info('Shutting down the engine')
        self.__up = False
        self.transport.tear_down()
