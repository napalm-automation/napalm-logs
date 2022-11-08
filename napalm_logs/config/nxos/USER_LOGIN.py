# -*- coding: utf-8 -*-
"""
Match messages AUTHPRIV-6-SYSTEM_MSG from NX-OS.

Message example:

.. code-block:: text

    sw01.bjm01: 2017 Jul 26 14:42:46 UTC: %AUTHPRIV-6-SYSTEM_MSG: pam_unix(dcos_sshd:session): session opened for user luke by (uid=0) - dcos_sshd[12977]  # noqa

Output example:

.. code-block:: json

    {
      "users": {
        "user": {
          "luke": {
            "action": {
              "login": true
            },
            "uid": 0
          }
        }
      }
    }
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from collections import OrderedDict

import napalm_logs.utils
from napalm_logs.config import OPEN_CONFIG_NO_MODEL

__tag__ = "AUTHPRIV-6-SYSTEM_MSG"
__error__ = "USER_LOGIN"
__yang_model__ = OPEN_CONFIG_NO_MODEL

log = logging.getLogger(__file__)

_RGX_PARTS = [("user", r"(\w+)"), ("uid", r"(\d+)"), ("sshPid", r"(\d+)")]
_RGX_PARTS = OrderedDict(_RGX_PARTS)

_RGX = (
    r"pam_unix\(dcos_sshd:session\): session opened for user "
    r"{0[user]} by \(uid={0[uid]}\) - dcos_sshd\[{0[sshPid]}\]"
).format(
    _RGX_PARTS
)  # ATTENTION to escape the parans


def emit(msg_dict):
    """
    Extracts the details from the syslog message
    and returns an object having the following structure:

    .. code-block:: python

        {
            u'users': {
                u'user': {
                    u'luke': {
                        u'action': {
                            u'login': True
                        },
                        u'uid': 0
                    }
                }
            }
        }
    """
    log.debug("Evaluating the message dict:")
    log.debug(msg_dict)
    ret = {}
    extracted = napalm_logs.utils.extract(_RGX, msg_dict["message"], _RGX_PARTS)
    if not extracted:
        return ret
    uid_key_path = "users//user//{0[user]}//uid".format(extracted)
    uid_value = int(extracted["uid"])
    log.debug("Setting %d under key path %s", uid_value, uid_key_path)
    ret.update(napalm_logs.utils.setval(uid_key_path, uid_value, dict_=ret))
    login_key_path = "users//user//{0[user]}//action//login".format(extracted)
    ret.update(napalm_logs.utils.setval(login_key_path, True, dict_=ret))
    return ret
