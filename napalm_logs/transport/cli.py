# -*- coding: utf-8 -*-
"""
CLI transport for napalm-logs.
Useful for debug only, publishes (prints) on the CLI.
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

# Import napalm-logs pkgs
from napalm_logs.transport.base import TransportBase


class CLITransport(TransportBase):
    """
    CLI transport class.
    """

    NO_ENCRYPT = True
    # This tells the publisher to not encrypt the messages
    #   published over this channel.

    def publish(self, obj):
        print(obj)
