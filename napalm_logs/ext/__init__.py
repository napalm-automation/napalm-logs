# -*- coding: utf-8 -*-
'''
External modules and functions.
'''
from __future__ import absolute_import

import re
import fnmatch
import logging

log = logging.getLogger(__name__)


def expr_match(line, expr):
    '''
    Evaluate a line of text against an expression. First try a full-string
    match, next try globbing, and then try to match assuming expr is a regular
    expression. Originally designed to match minion IDs for
    whitelists/blacklists.
    '''
    if line == expr:
        return True
    if fnmatch.fnmatch(line, expr):
        return True
    try:
        if re.match(r'\A{0}\Z'.format(expr), line):
            return True
    except re.error:
        pass
    return False


def check_whitelist_blacklist(value, whitelist=None, blacklist=None):
    '''
    Check a whitelist and/or blacklist to see if the value matches it.

    value
        The item to check the whitelist and/or blacklist against.

    whitelist
        The list of items that are white-listed. If ``value`` is found
        in the whitelist, then the function returns ``True``. Otherwise,
        it returns ``False``.

    blacklist
        The list of items that are black-listed. If ``value`` is found
        in the blacklist, then the function returns ``False``. Otherwise,
        it returns ``True``.

    If both a whitelist and a blacklist are provided, value membership
    in the blacklist will be examined first. If the value is not found
    in the blacklist, then the whitelist is checked. If the value isn't
    found in the whitelist, the function returns ``False``.
    '''
    if blacklist is not None:
        if not hasattr(blacklist, '__iter__'):
            blacklist = [blacklist]
        try:
            for expr in blacklist:
                if expr_match(value, expr):
                    return False
        except TypeError:
            log.error('Non-iterable blacklist {0}'.format(blacklist))

    if whitelist:
        if not hasattr(whitelist, '__iter__'):
            whitelist = [whitelist]
        try:
            for expr in whitelist:
                if expr_match(value, expr):
                    return True
        except TypeError:
            log.error('Non-iterable whitelist {0}'.format(whitelist))
    else:
        return True

    return False
