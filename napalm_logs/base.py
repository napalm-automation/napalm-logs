# -*- coding: utf-8 -*-
'''
napalm-logs base
'''
from __future__ import absolute_import

# Import std lib
import os
import re
import ssl
import time
import yaml
import signal
import socket
import logging
import threading
from multiprocessing import Process, Pipe

# Import third party libs
### crypto
import nacl.utils
import nacl.secret
import nacl.signing
import nacl.encoding

# Import napalm-logs pkgs
import napalm_logs.config as CONFIG
from napalm_logs.listener import get_listener
# processes
from napalm_logs.auth import NapalmLogsAuthProc
from napalm_logs.device import NapalmLogsDeviceProc
from napalm_logs.server import NapalmLogsServerProc
from napalm_logs.publisher import NapalmLogsPublisherProc
# exceptions
from napalm_logs.exceptions import BindException
from napalm_logs.exceptions import ConfigurationException

log = logging.getLogger(__name__)


class NapalmLogs:
    def __init__(self,
                 address='0.0.0.0',
                 port=514,
                 listener='udp',
                 transport='zmq',
                 publish_address='0.0.0.0',
                 publish_port=49017,
                 auth_address='0.0.0.0',
                 auth_port=49018,
                 certificate=None,
                 keyfile=None,
                 disable_security=False,
                 config_path=None,
                 config_dict=None,
                 extension_config_path=None,
                 extension_config_dict=None,
                 log_level='warning',
                 log_format='%(asctime)s,%(msecs)03.0f [%(name)-17s][%(levelname)-8s] %(message)s'):
        '''
        Init the napalm-logs engine.

        :param address: The address to bind the syslog client. Default: 0.0.0.0.
        :param port: Listen port. Default: 514.
        :param listener: Listen type. Default: udp.
        :param publish_address: The address to bing when publishing the OC
                                 objects. Default: 0.0.0.0.
        :param publish_port: Publish port. Default: 49017.
        '''
        self.address = address
        self.port = port
        self.listener = listener
        self.publish_address = publish_address
        self.publish_port = publish_port
        self.auth_address = auth_address
        self.auth_port = auth_port
        self.certificate = certificate
        self.keyfile = keyfile
        self.disable_security = disable_security
        self.config_path = config_path
        self.config_dict = config_dict
        self.transport = transport
        self.extension_config_path = extension_config_path
        self.extension_config_dict = extension_config_dict
        self.log_level = log_level
        self.log_format = log_format
        # Setup the environment
        self._setup_log()
        self._build_config()
        self._verify_config()
        # Private vars
        self.__priv_key = None
        self.__signing_key = None
        self._processes = []

    def _exit_gracefully(self, signum, _):
        self.stop_engine()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stop_engine()
        if exc_type is not None:
            log.error('Exiting due to unhandled exception', exc_info=True)
            self.__raise_clean_exception(exc_type, exc_value, exc_traceback)

    def _setup_log(self):
        '''
        Setup the log object.
        '''
        logging_level = CONFIG.LOGGING_LEVEL.get(self.log_level.lower())
        logging.basicConfig(format=self.log_format,
                            level=logging_level)

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

    @staticmethod
    def _raise_config_exception(error_string):
        log.error(error_string, exc_info=True)
        raise ConfigurationException(error_string)

    def _compare_values(self, value, config, dev_os, key_path):
        if 'line' not in value.keys() or 'values' not in value.keys():
            return
        from_line = re.findall('\{(\w+)\}', config['line'])
        if set(from_line) == set(config['values']):
            return
        if config.get('error'):
            error = 'The "values" do not match variables in "line" for {}:{} in {}'.format(
                ':'.join(key_path),
                config.get('error'),
                dev_os
                )
        else:
            error = 'The "values" do not match variables in "line" for {} in {}'.format(
                ':'.join(key_path),
                dev_os
                )
        self._raise_config_exception(error)

    def _verify_config_key(self, key, value, valid, config, dev_os, key_path):
        key_path.append(key)
        if config.get(key, False) is False:
            self._raise_config_exception(
                'Unable to find key "{}" for {}'.format(':'.join(key_path), dev_os))
        if isinstance(value, type):
            if not isinstance(config[key], value):
                self._raise_config_exception(
                    'Key "{}" for {} should be {}'.format(':'.join(key_path), dev_os, value))
        elif isinstance(value, dict):
            if not isinstance(config[key], dict):
                self._raise_config_exception(
                    'Key "{}" for {} should be of type <dict>'.format(':'.join(key_path), dev_os))
            self._verify_config_dict(value, config[key], dev_os, key_path)
            # As we have already checked that the config below this point is correct, we know that "line" and "values"
            # exists in the config if they are present in the valid config
            self._compare_values(value, config[key], dev_os, key_path)
        elif isinstance(value, list):
            if not isinstance(config[key], list):
                self._raise_config_exception(
                    'Key "{}" for {} should be of type <list>'.format(':'.join(key_path), dev_os))
            for item in config[key]:
                self._verify_config_dict(value[0], item, dev_os, key_path)
                self._compare_values(value[0], item, dev_os, key_path)
        key_path.remove(key)

    def _verify_config_dict(self, valid, config, dev_os, key_path=None):
        '''
        Verify if the config dict is valid.
        '''
        if not key_path:
            key_path = []
        for key, value in valid.items():
            self._verify_config_key(key, value, valid, config, dev_os, key_path)

    def _verify_config(self):
        '''
        Verify that the config is correct
        '''
        if not self.config_dict:
            self._raise_config_exception('No config found')
        # Check for device conifg, if there isn't anything then just log, do not raise an exception
        for dev_os, dev_config in self.config_dict.items():
            if not dev_config:
                log.warning('No config found for {}'.format(dev_os))
                continue
            # Compare the valid opts with the conifg
            self._verify_config_dict(CONFIG.VALID_CONFIG, dev_config, dev_os)
        log.debug('Read the config without error \o/')

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

    def _respawn_when_dead(self, start_fun, *args, **kwargs):
        '''
        Start a process and restart when dead.
        '''
        proc = start_fun(*args, **kwargs)
        pid = proc.pid
        log.debug('Starting keepalive for {pname} ({pid})'.format(
                pname=proc._name,
                pid=pid
            )
        )
        while True:
            time.sleep(5)
            proc_file = os.path.join('/proc', str(pid), 'stat')
            try:
                proc_flag = open(proc_file).readline().split()[2]
            except IOError:
                log.warning('The following error may not be critical:')
                log.warning('Unable to read {0}'.format(proc_file), exc_info=True)
                proc_flag = 'X'
            if proc_flag in CONFIG.PROC_DEAD_FLAGS:
                log.warning('Process {pname} with {pid} is dead, restarting'.format(
                        pname=proc._name,
                        pid=pid
                    )
                )
                log.debug('Killing the previous process')
                try:
                    os.kill(pid, 9)
                except OSError as err:
                    log.error('Unable to kill {0}'.format(pid))
                    if err.strerror == 'No such process':
                        log.warning('The following error may not be critical:')
                        log.warning('Unable to kill PID {0}'.format(pid), exc_info=True)
                # Restarting proc
                proc = start_fun(*args, **kwargs)
                log.warning('{pname} {prev_pid} restarted as PID {pid}'.format(
                        pname=proc._name,
                        prev_pid=pid,
                        pid=proc.pid
                    )
                )
                pid = proc.pid

    def _start_auth_proc(self, auth_skt):
        '''
        Start the authenticator process.
        '''
        log.debug('Computing the signing key hex')
        verify_key = self.__signing_key.verify_key
        sgn_verify_hex = verify_key.encode(encoder=nacl.encoding.HexEncoder)
        log.debug('Starting the authenticator subprocess')
        auth = NapalmLogsAuthProc(self.certificate,
                                  self.keyfile,
                                  self.__priv_key,
                                  sgn_verify_hex,
                                  auth_skt)
        auth.verify_cert()
        proc = Process(target=auth.start)
        proc.start()
        log.debug('Started auth process as {pname} with PID {pid}'.format(
                pname=proc._name,
                pid=proc.pid
            )
        )
        return proc

    def _start_lst_proc(self, address, port, listener, pipe):
        '''
        Start the listener process.
        '''
        log.debug('Starting the listener process')
        # Get the correct listener class
        listener_class = get_listener(self.listener)
        listener = listener_class(address, port, pipe)
        proc = Process(target=listener.start)
        proc.start()
        log.debug('Started listener process as {pname} with PID {pid}'.format(
                pname=proc._name,
                pid=proc.pid
            )
        )
        return proc

    def _start_srv_proc(self, pipe, os_pipes):
        '''
        Start the server process.
        '''
        log.debug('Starting the server process')
        server = NapalmLogsServerProc(self.config_dict,
                                      pipe,
                                      os_pipes)
        proc = Process(target=server.start)
        proc.start()
        log.debug('Started server process as {pname} with PID {pid}'.format(
                pname=proc._name,
                pid=proc.pid
            )
        )
        return proc

    def _start_pub_proc(self, pub_pipe):
        '''
        Start the publisher process.
        '''
        log.info('Starting the publisher process')
        publisher = NapalmLogsPublisherProc(self.publish_address,
                                            self.publish_port,
                                            self.transport,
                                            pub_pipe,
                                            self.__priv_key,
                                            self.__signing_key,
                                            disable_security=self.disable_security)
        proc = Process(target=publisher.start)
        proc.start()
        log.debug('Started publisher process as {pname} with PID {pid}'.format(
                pname=proc._name,
                pid=proc.pid
            )
        )
        return proc

    def _start_dev_proc(self,
                        device_os,
                        device_config,
                        device_pipe,
                        dev_pub_pipe):
        '''
        Start the device worker process.
        '''
        # TODO remove the pipe overhead when migrating to zmq IPC
        log.info('Starting the child process for {dos}'.format(dos=device_os))
        dos = NapalmLogsDeviceProc(device_os,
                                   device_config,
                                   device_pipe,
                                   dev_pub_pipe)
        os_proc = Process(target=dos.start)
        os_proc.start()
        log.debug('Started process {pname} for {dos}, having PID {pid}'.format(
                pname=os_proc._name,
                dos=device_os,
                pid=os_proc.pid
            )
        )
        return os_proc

    def start_engine(self):
        '''
        Start the child processes (one per device OS)
        '''
        # main listener socket
        # auth proc section
        log.debug('Creating the auth socket')
        if ':' in self.auth_address:
            auth_skt = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            auth_skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            auth_skt.bind((self.auth_address, self.auth_port))
        except socket.error as msg:
            error_string = 'Unable to bind (auth) to port {} on {}: {}'.format(self.auth_port, self.auth_address, msg)
            log.error(error_string, exc_info=True)
            raise BindException(error_string)
        if self.disable_security is True:
            log.warning('***Not starting the authenticator process due to disable_security being set to True***')
        else:
            log.debug('Generating the private key')
            self.__priv_key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
            log.debug('Generating the signing key')
            self.__signing_key = nacl.signing.SigningKey.generate()
            # start the keepalive thread for the auth sub-process
            self._processes.append(self._start_auth_proc(auth_skt))
        # publisher process start
        pub_pipe, dev_pub_pipe = Pipe(duplex=False)
        self._processes.append(self._start_pub_proc(pub_pipe))
        # device process start
        log.info('Starting child processes for each device type')
        os_pipes = {}
        for device_os, device_config in self.config_dict.items():
            device_pipe, srv_pipe = Pipe(duplex=False)
            self._processes.append(self._start_dev_proc(device_os,
                                   device_config,
                                   device_pipe,
                                   dev_pub_pipe))
            os_pipes[device_os] = srv_pipe
        # start server process
        srv_pipe, lst_pipe = Pipe(duplex=False)
        self._processes.append(self._start_srv_proc(srv_pipe, os_pipes))
        # start listener process
        self._processes.append(self._start_lst_proc(self.address,
                                                    self.port,
                                                    self.listener,
                                                    lst_pipe))

    def stop_engine(self):
        log.info('Shutting down the engine')
        # Set SIGTERM to all child processes, then join them
        for proc in self._processes:
            proc.terminate()
        for proc in self._processes:
            proc.join()
