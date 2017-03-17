# -*- coding: utf-8 -*-
'''
napalm-logs base
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import napalm-logs pkgs
from napalm_logs.transport import get_transport


class NapalmLogs:
    def __init__(self,
                 hostname='0.0.0.0',
                 port=514,
                 transport='zmq',
                 publish_hostname='0.0.0.0',
                 publish_port=49017):
        '''
        Init the napalm-logs engine.

        :param hostname: The address to bind the syslog client. Default: 0.0.0.0.
        :param port: Listen port. Default: 514.
        :param publish_hostname: The address to bing when publishing the OC
                                 objects. Default: 0.0.0.0.
        :param publish_port: Publish port. Default: 49017.
        '''
        # TODO the other stuff
        self.hostname = hostname
        self.port = port
        self.publish_hostname = publish_hostname
        self.publish_port = publish_port
        transport_class = get_transport(transport)
        self.transport = transport_class(self.publish_hostname,
                                         self.publish_port)

    def _load_config(self):
        '''
        Read the config of the napalm engine listener.
        Then, it loads the configuration of the
        '''
        pass

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

    def _parse_message(self, msg):
        '''
        Parse a syslog message and check what OpenConfig object should
        be generated.
        '''
        pass

    def _emit_oc(self, **kwargs):
        '''
        Emit an OpenConfig object given a certain combination of
        fields mappeed in the config to the corresponding hierarchy.
        '''
        pass

    def _publish_oc_obj(self, obj):
        '''
        Publish the OC object.
        '''
        self.transport.publish(obj)

    def start_engine(self):
        '''
        Start listening to syslog messages.
        '''
