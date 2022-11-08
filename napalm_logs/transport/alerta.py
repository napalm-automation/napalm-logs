# -*- coding: utf-8 -*-
"""
Alerta publisher for napalm-logs.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

# Import napalm-logs pkgs
import napalm_logs.utils
from napalm_logs.transport.http import HTTPTransport

# As defined in https://docs.alerta.io/en/latest/api/alert.html#severity-table
ALERTA_SEVERITY = {
    0: "security",
    1: "critical",
    2: "major",
    3: "minor",
    4: "warning",
    5: "informational",
    6: "debug",
    7: "trace",
    8: "indeterminate",
    9: "normal",
    10: "unknown",
}


class AlertaTransport(HTTPTransport):
    """
    Alerta publisher class.
    """

    def __init__(self, address, port, **kwargs):
        super().__init__(address, port, **kwargs)
        if not self.address.endswith("/alert") and not self.address.endswith("/alert/"):
            self.address = "{}/alert".format(self.address)
        self.method = "POST"
        self.headers["Content-type"] = "application/json"
        key = kwargs.get("key")
        if key and "Authorization" not in self.headers:
            self.headers.update({"Authorization": "Key {}".format(key)})
        token = kwargs.get("token")
        if token and "Authorization" not in self.headers:
            self.headers.update({"Authorization": "Bearer {}".format(token)})
        self.environment = kwargs.get("environment")
        self.pairs = kwargs.get("pairs")
        if not self.pairs:
            self.pairs = {
                "INTERFACE_UP": "INTERFACE_DOWN",
                "OSPF_NEIGHBOR_UP": "OSPF_NEIGHBOR_DOWN",
                "ISIS_NEIGHBOR_UP": "ISIS_NEIGHBOR_DOWN",
            }

    def publish(self, obj):
        data = napalm_logs.utils.unserialize(obj)
        error = data["error"]
        status = "open"
        if error in self.pairs:
            error = self.pairs[error]
            status = "closed"
        alerta_data = {
            "resource": "{host}::{msg}".format(host=data["host"], msg=error),
            "event": data["error"],
            "service": ["napalm-logs"],
            "text": data["message_details"]["message"].strip(),
            "attributes": data,
            "status": status,
        }
        if self.environment:
            alerta_data["environment"] = self.environment
        alerta_data["severity"] = ALERTA_SEVERITY.get(data["severity"], "unknown")
        if self.backend == "tornado":
            self.tornado_client.fetch(
                self.address,
                callback=self._handle_tornado_response,
                method=self.method,
                headers=self.headers,
                auth_username=self.username,
                auth_password=self.password,
                body=str(alerta_data),
                validate_cert=self.verify_ssl,
                allow_nonstandard_methods=True,
                decompress_response=False,
            )
        elif self.backend == "requests":
            # Queue the publish object async
            self._publish_queue.put_nowait(alerta_data)
