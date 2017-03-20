# -*- coding: utf-8 -*-
'''
napalm-logs base worker process
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import pythond stdlib
import os
import time


class NapalmLogsProc:
    def _suicide_when_without_parent(self, parent_pid):
        '''
        Kill this process when the parent died.
        '''
        while True:
            time.sleep(5)
            try:
                # Check pid alive
                os.kill(parent_pid, 0)
            except OSError:
                # Forcibly exit
                # Regular sys.exit raises an exception
                os._exit(999)
