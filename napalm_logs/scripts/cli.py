#!/usr/bin/env python
'''
Kick off the napalm-logs engine.
'''

# Import python stdlib
import os
import sys
import time
import signal
import logging
import optparse

# Import third party libs
import yaml

# Import napalm-logs
import napalm_logs
import napalm_logs.config as defaults

log = logging.getLogger(__name__)


class CustomOption(optparse.Option, object):
    def take_action(self, action, dest, *args, **kwargs):
        # see https://github.com/python/cpython/blob/master/Lib/optparse.py#L786
        self.explicit = True
        return optparse.Option.take_action(self, action, dest, *args, **kwargs)


class OptionParser(optparse.OptionParser, object):

    VERSION = napalm_logs.__version__
    usage = 'napalm-logs [options]'
    epilog = 'Full documentation coming soon.'
    description = 'napalm-logs CLI script.'

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('version', '%prog {0}'.format(self.VERSION))
        kwargs.setdefault('usage', self.usage)
        kwargs.setdefault('description', self.description)
        kwargs.setdefault('epilog', self.epilog)
        kwargs.setdefault('option_class', CustomOption)
        optparse.OptionParser.__init__(self, *args, **kwargs)
        self.add_option(
            '-v',
            action='store_true',
            dest='version',
            help='Show version number and exit.'
        )

    def add_option_group(self, *args, **kwargs):
        option_group = optparse.OptionParser.add_option_group(self, *args, **kwargs)
        option_group.option_class = CustomOption
        return option_group

    def parse_args(self, args=None, values=None):
        options, args = optparse.OptionParser.parse_args(self, args, values)
        if 'args_stdin' in options.__dict__ and options.args_stdin is True:
            new_inargs = sys.stdin.readlines()
            new_inargs = [arg.rstrip('\r\n') for arg in new_inargs]
            new_options, new_args = optparse.OptionParser.parse_args(
                self,
                new_inargs)
            options.__dict__.update(new_options.__dict__)
            args.extend(new_args)
        self.options, self.args = options, args

    def print_version(self):
        print('napalm-logs {0}'.format(self.VERSION))


class NLOptionParser(OptionParser, object):
    def prepare(self):
        self.add_option(
            '-c', '--config-file',
            dest='config_file',
            help=('Config file absolute path. Default: {0}'.format(defaults.CONFIG_FILE))
        )
        # self.add_option(
        #     '-d', '--daemon',
        #     default=True,
        #     dest='daemon',
        #     action='store_true',
        #     help='Run the {0} as a daemon. Default: %default'.format(self.get_prog_name())
        # )
        self.add_option(
            '-a', '--address',
            dest='address',
            help=('Listener address. Default: {0}'.format(defaults.ADDRESS))
        )
        self.add_option(
            '--config-path',
            dest='config_path',
            help=('Extension device config path.')
        )
        self.add_option(
            '--extension-config-path',
            dest='extension_config_path',
            help=('Extension config path.')
        )
        self.add_option(
            '-p', '--port',
            dest='port',
            type=int,
            help=('Listener bind port. Default: {0}'.format(defaults.PORT))
        )
        self.add_option(
            '--listener',
            dest='listener',
            choices=['kafka', 'tcp', 'udp'],
            help=('Listener type. Default: {0}'.format(defaults.LISTENER))
        )
        self.add_option(
            '-t', '--transport',
            default='zmq',
            dest='transport',
            help=('Publish transport. Default: %default')
        )
        self.add_option(
            '--publish-address',
            dest='publish_address',
            help=('Publisher bind address. Default: {0}'.format(defaults.PUBLISH_ADDRESS))
        )
        self.add_option(
            '--publish-port',
            dest='publish_port',
            type=int,
            help=('Publisher bind port. Default: {0}'.format(defaults.PUBLISH_PORT))
        )
        self.add_option(
            '--auth-address',
            dest='auth_address',
            help=('Authenticator bind address. Default: {0}'.format(defaults.AUTH_ADDRESS))
        )
        self.add_option(
            '--auth-port',
            dest='auth_port',
            type=int,
            help=('Authenticator bind port. Default: {0}'.format(defaults.AUTH_PORT))
        )
        self.add_option(
            '--certificate',
            dest='certificate',
            help=('Absolute path to the SSL certificate used for client authentication.')
        )
        self.add_option(
            '--keyfile',
            dest='keyfile',
            help=('Absolute path to the SSL keyfile')
        )
        self.add_option(
            '--disable-security',
            dest='disable_security',
            action="store_true",
            default=False,
            help=('Disable encryption and data signing when publishing.')
        )
        self.add_option(
            '-l', '--log-level',
            default='warning',
            dest='log_level',
            help=('Logging level. Default: {0}'.format(defaults.LOG_LEVEL))
        )
        self.add_option(
            '--log-file',
            dest='log_file',
            help=('Logging file. Default: {0}'.format(defaults.LOG_FILE))
        )
        self.add_option(
            '--log-format',
            dest='log_format',
            help=('Logging format. Default: {0}'.format(defaults.LOG_FORMAT))
        )

    @staticmethod
    def read_config_file(filepath):
        config = {}
        try:
            with open(filepath, 'r') as fstream:
                config = yaml.load(fstream)
        except (IOError, yaml.YAMLError):
            log.info('Unable to read from {0}'.format(filepath))
        return config

    def parse(self, log, screen_handler):
        self.prepare()
        self.parse_args()
        if self.options.version:
            self.print_version()
            sys.exit(1)
        config_file_path = self.options.config_file or defaults.CONFIG_FILE
        file_cfg = self.read_config_file(config_file_path)
        log_file = self.options.log_file or file_cfg.get('log_file') or defaults.LOG_FILE
        log_lvl = self.options.log_level or file_cfg.get('log_level') or defaults.LOG_LEVEL
        log_fmt = self.options.log_format or file_cfg.get('log_format') or defaults.LOG_FORMAT
        if log_file.lower() not in defaults.LOG_FILE_CLI_OPTIONS:
            log_file_dir = os.path.dirname(log_file)
            if not os.path.isdir(log_file_dir):
                log.warning('{0} does not exist, trying to create'.format(log_file_dir))
                try:
                    os.mkdir(log_file_dir)
                except OSError:
                    log.error('Unable to create {0}'.format(log_file_dir), exc_info=True)
                    sys.exit(0)
            log.removeHandler(screen_handler)  # remove printing to the screen
            logging.basicConfig(filename=log_file,
                                level=defaults.LOGGING_LEVEL.get(log_lvl.lower(), 'warning'),
                                format=log_fmt)  # log to filecm
        cert = self.options.certificate or file_cfg.get('certificate')
        if not cert and self.options.disable_security is False:
            log.error('certfile must be specified for server-side operations')
            raise ValueError('Please specify a valid SSL certificate.')
        cfg = {
            'address': self.options.address or file_cfg.get('address') or defaults.ADDRESS,
            'port': self.options.port or file_cfg.get('port') or defaults.PORT,
            'listener': self.options.listener or file_cfg.get('listener') or defaults.LISTENER,
            'transport': self.options.transport or file_cfg.get('transport'),
            'publish_address': self.options.publish_address or file_cfg.get('publish_address')\
                               or defaults.PUBLISH_ADDRESS,
            'publish_port': self.options.publish_port or file_cfg.get('publish_port')\
                            or defaults.PUBLISH_PORT,
            'auth_address': self.options.auth_address or file_cfg.get('auth_address')\
                               or defaults.AUTH_ADDRESS,
            'auth_port': self.options.auth_port or file_cfg.get('auth_port')\
                            or defaults.AUTH_PORT,
            'certificate': cert,
            'keyfile': self.options.keyfile or file_cfg.get('keyfile'),
            'disable_security': self.options.disable_security or file_cfg.get('disable_security'),
            'config_path': self.options.config_path or file_cfg.get('config_path'),
            'extension_config_path': self.options.extension_config_path or file_cfg.get('extension_config_path'),
            'log_level': log_lvl,
            'log_format': log_fmt
        }
        return cfg


def _exit_gracefully(signum, _):
    ''' 
    Called when a signal is caught and marks exiting variable True
    '''
    global _up
    _up = False

_up = True

def napalm_logs_engine():
    if '' in sys.path:
        sys.path.remove('')
    # Temporarily will forward the log entries to the screen
    # After reading the config and all good, will write into the right
    # log file.
    screen_logger = logging.StreamHandler(sys.stdout)
    screen_logger.setFormatter(logging.Formatter(defaults.LOG_FORMAT))
    log.addHandler(screen_logger)
    nlop = NLOptionParser()
    config = nlop.parse(log, screen_logger)
    # Ignore SIGINT whilst starting child processes so they inherit the ignore
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    nl = napalm_logs.NapalmLogs(**config)
    nl.start_engine()
    # Set SIGINT to _exit_gracefully so we can close everything down gracefully
    signal.signal(signal.SIGINT, _exit_gracefully)
    # Keep this function running until we receive instruction to terminate
    while _up is True:
        time.sleep(1)
    nl.stop_engine()

if __name__ == '__main__':
    napalm_logs_engine()
