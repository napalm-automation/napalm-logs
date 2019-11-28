# -*- coding: utf-8 -*-
'''
Test the napalm-logs base class.
'''
from __future__ import absolute_import
from __future__ import unicode_literals

from napalm_logs.utils import bgp_state_convert, bfd_state_convert


def test_bgp_state_convert_in_dict():
    """
    Test bgp_state_convert returns values from its internal dict
    """
    assert bgp_state_convert('OpenSent') == 'OPEN_SENT'
    assert bgp_state_convert('OpenConfirm') == 'OPEN_CONFIRM'


def test_bgp_state_convert_not_dict():
    """
    Test bgp_state_convert returns upper values for items not in
    its internal dict
    """
    assert bgp_state_convert('Connect') == 'CONNECT'


def test_bfd_state_convert_in_dict():
    """
    Test bfd_state_convert returns values from its internal dict
    """
    assert bfd_state_convert('AdminDown') == 'ADMIN_DOWN'


def test_bfd_state_convert_not_dict():
    """
    Test bfd_state_convert returns upper values for items not in
    its internal dict
    """
    assert bfd_state_convert('Up') == 'UP'
