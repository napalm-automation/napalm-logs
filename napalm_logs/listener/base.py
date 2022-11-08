# -*- coding: utf-8 -*-
"""
napalm-logs listener base.
"""


class ListenerBase:
    """
    The base class for the listener.
    """

    def __init__(self, address, port, **kwargs):
        pass

    def start(self):
        """
        Starts the listener.
        """
        pass

    def receive(self):
        """
        Return an object read from the source,
        and the location identification object.
        """
        pass

    def stop(self):
        """
        Shuts down the listener.
        """
        pass
