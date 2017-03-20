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
from multiprocessing import Process, Pipe

# Import napalm-logs pkgs
import napalm_logs.exceptions
from napalm_logs.transport import get_transport
from napalm_logs.device import NapalmLogsDeviceProc
from napalm_logs.server import NapalmLogsServerProc
from napalm_logs.listener import NapalmLogsListenerProc

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
                 extension_config_dict=None,
                 log_level='warning',
                 log_fmt='%(asctime)s,%(msecs)03.0f [%(name)-17s][%(levelname)-8s] %(message)s'):
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
        self._transport_type = transport
        self.extension_config_path = extension_config_path
        self.extension_config_dict = extension_config_dict
        self.log_level = log_level
        self.log_fmt = log_fmt
        # Setup the environment
        self._setup_log()
        self._setup_transport()
        self._build_config()
        self._precompile_regex()
        # Private vars
        self.__os_proc_map = {}

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stop_engine()
        if exc_type is not None:
            log.error('Exiting due to unhandled exception', exc_info=True)
            self.__raise_clean_exception(exc_type, exc_value, exc_traceback)

    def __del__(self):
        self.stop_engine()

    def _setup_log(self):
        '''
        Setup the log object.
        '''
        logging_level = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }.get(self.log_level.lower())
        logging.basicConfig(format=self.log_fmt,
                            level=logging_level)

    def _setup_transport(self):
        '''
        Setup the transport.
        '''
        transport_class = get_transport(self._transport_type)
        self.transport = transport_class(self.publish_hostname,
                                         self.publish_port)

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
                log.error('Invalid YAML file: {}'.format(filepath), exc_info=True)
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

    def start_engine(self):
        '''
        Start the child processes (one per device OS),
        open the socket to start receiving messages.
        '''
        # TODO prepare the binding to be able to listen to syslog messages
        log.info('Preparing the transport')
        self.transport.start()
        log.info('Starting child processes for each device type')
        os_pipe_map = {}
        for device_os, device_config in self.config_dict.items():
            parent_pipe, child_pipe = Pipe()
            log.debug('Initialized pipe for {dos}'.format(dos=device_os))
            log.debug('Parent handle is {phandle} ({phash})'.format(phandle=str(parent_pipe),
                                                                    phash=hash(parent_pipe)))
            log.debug('Child handle is {chandle} ({chash})'.format(chandle=str(child_pipe),
                                                                    chash=hash(child_pipe)))
            log.info('Starting the child process for {dos}'.format(dos=device_os))
            dos = NapalmLogsDeviceProc(device_os,
                                       device_config,
                                       self.transport,
                                       child_pipe)
            os_pipe_map[device_os] = parent_pipe
            os_proc = Process(target=dos.start)
            os_proc.start()
            log.debug('Started process {pname} for {dos}, having PID {pid}'.format(
                    pname=os_proc._name,
                    dos=device_os,
                    pid=os_proc.pid
                )
            )
            self.__os_proc_map[device_os] = os_proc
        log.debug('Setting up the syslog pipe')
        listen_pipe, serve_pipe = Pipe()
        log.debug('Starting the server process')
        server = NapalmLogsServerProc(serve_pipe,
                                      os_pipe_map,
                                      self.config_dict)
        pserve = Process(target=server.start)
        pserve.start()
        log.debug('Started server process as {pname} with PID {pid}'.format(
                pname=pserve._name,
                pid=pserve.pid
            )
        )
        log.debug('Starting the listener process')
        listener = NapalmLogsListenerProc(self.hostname,
                                          self.port,
                                          listen_pipe)
        plisten = Process(target=listener.start)
        plisten.start()
        log.debug('Started listener process as {pname} with PID {pid}'.format(
                pname=plisten._name,
                pid=pserve.pid
            )
        )

    def stop_engine(self):
        log.info('Shutting down the engine')
        if hasattr(self, 'transport'):
            self.transport.tear_down()
