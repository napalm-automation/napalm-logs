# -*- coding: utf-8 -*-
'''
Base worker process
'''
from __future__ import absolute_import
from __future__ import unicode_literals

# Import pythond stdlib
import os
import time
import logging

log = logging.getLogger(__name__)


class NapalmLogsProc:
    '''
    Sub-process base class.
    '''
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
                log.warning('The parent is not alive, exiting.')
                os._exit(999)
