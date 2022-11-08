# -*- coding: utf-8 -*-
"""
Export napalm-logs notifications as Prometheus metrics.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

# Import stdlib
import logging

# Import third party libs
from prometheus_client import Counter, Gauge

# Import napalm-logs pkgs
import napalm_logs.utils
from napalm_logs.transport.base import TransportBase

log = logging.getLogger(__name__)


class PrometheusTransport(TransportBase):
    """
    Prom transport class.
    """

    def __init__(self, address, port, **kwargs):
        self.metrics = {}

    def __parse_without_details(self, msg):
        """
        Helper to generate Counter metrics that only provide the host label
        from the structured message.
        """
        error = msg["error"]
        if error not in self.metrics:
            self.metrics[error] = Counter(
                "napalm_logs_{error}".format(error=error.lower()),
                "Counter for {error} notifications".format(error=error),
                ["host"],
            )
        self.metrics[error].labels(host=msg["host"]).inc()

        if msg.get("state") is not None:
            base = error.split("_")[:-1]
            metric = msg.get("state_tag", "_".join(base + ["state"]).lower())
            if metric not in self.metrics:
                self.metrics[metric] = Gauge(
                    "napalm_logs_{}".format(metric),
                    "State for {} type notifications".format("_".join(base)),
                    ["host"],
                )
            self.metrics[metric].labels(host=msg["host"]).set(msg["state"])

    def __parse_user_action(self, msg):
        """
        Helper to generate Counter metrics that provide the host label, together
        with the username under a YANG structure users > user > [USER].
        """
        error = msg["error"]
        if error not in self.metrics:
            self.metrics[error] = Counter(
                "napalm_logs_{error}".format(error=error.lower()),
                "Counter for {error} notifications".format(error=error),
                ["host", "user"],
            )
        self.metrics[error].labels(
            host=msg["host"], user=list(msg["yang_message"]["users"]["user"].keys())[0]
        ).inc()

    def __parse_interface_basic(self, msg):
        """
        Helper to generate Counter metrics for interface notifications.
        """
        error = msg["error"]
        if error not in self.metrics:
            self.metrics[error] = Counter(
                "napalm_logs_{error}".format(error=error.lower()),
                "Counter for {error} notifications".format(error=error),
                ["host", "interface"],
            )
        if "interface_state" not in self.metrics:
            self.metrics["interface_state"] = Gauge(
                "napalm_logs_interface_state",
                "State of this interface. 0=DOWN, 1=UP",
                ["host", "interface"],
            )
        labels = {
            "host": msg["host"],
            "interface": list(msg["yang_message"]["interfaces"]["interface"].keys())[0],
        }
        self.metrics[error].labels(**labels).inc()
        state = 1 if error == "INTERFACE_UP" else 0
        self.metrics["interface_state"].labels(**labels).set(state)

    def __parse_lacp(self, msg):
        """
        Helper to generate Counter metrics for LACP notifications.
        """
        error = msg["error"]
        if error not in self.metrics:
            self.metrics[error] = Counter(
                "napalm_logs_{error}".format(error=error.lower()),
                "Counter for {error} notifications".format(error=error),
                ["host", "interface", "member"],
            )
        lacp_dict = msg["yang_message"]["lacp"]["interfaces"]["interface"]
        if_name = list(lacp_dict.keys())[0]
        members_dict = lacp_dict[if_name]["members"]["member"]
        member_name = list(members_dict.keys())[0]
        self.metrics[error].labels(
            host=msg["host"], interface=if_name, member=member_name
        ).inc()

    def __parse_bgp_basic(self, msg):
        """
        Helper to generate Counter metrics for simple BGP notifications,
        providing the neighbor address and peer AS number.
        """
        error = msg["error"]
        if error not in self.metrics:
            self.metrics[error] = Counter(
                "napalm_logs_{error}".format(error=error.lower()),
                "Counter for {error} notifications".format(error=error),
                ["host", "neighbor", "peer_as"],
            )
        neigh_dict = msg["yang_message"]["bgp"]["neighbors"]["neighbor"]
        neighbor = list(neigh_dict.keys())[0]
        self.metrics[error].labels(
            host=msg["host"],
            neighbor=neighbor,
            peer_as=neigh_dict[neighbor]["state"]["peer_as"],
        ).inc()

    def __parse_network_instance_bgp(self, msg):
        """
        Helper to generate Counter metrics for simple BGP notifications, nested
        under the network-instance OpenConfig model, providing the neighbor
        address, instance name, and peer AS number.
        """
        error = msg["error"]
        if error not in self.metrics:
            self.metrics[error] = Counter(
                "napalm_logs_{error}".format(error=error.lower()),
                "Counter for {error} notifications".format(error=error),
                ["host", "routing_instance", "neighbor", "peer_as"],
            )
        instance_name = list(
            msg["yang_message"]["network-instances"]["network-instance"].keys()
        )[0]
        instance_dict = msg["yang_message"]["network-instances"]["network-instance"][
            instance_name
        ]
        neigh_dict = instance_dict["protocols"]["protocol"]["bgp"]["neighbors"][
            "neighbor"
        ]
        neighbor = list(neigh_dict.keys())[0]
        self.metrics[error].labels(
            host=msg["host"],
            routing_instance=instance_name,
            neighbor=neighbor,
            peer_as=neigh_dict[neighbor]["state"]["peer_as"],
        ).inc()

    def __parse_bgp_no_asn(self, msg):
        """
        Helper to generate Counter metrics for simple BGP notifications - but
        without the AS number, so only the neighbor IP address.
        """
        error = msg["error"]
        if error not in self.metrics:
            self.metrics[error] = Counter(
                "napalm_logs_{error}".format(error=error.lower()),
                "Counter for {error} notifications".format(error=error),
                ["host", "neighbor"],
            )
        neigh_dict = msg["yang_message"]["bgp"]["neighbors"]["neighbor"]
        neighbor = list(neigh_dict.keys())[0]
        self.metrics[error].labels(
            host=msg["host"],
            neighbor=neighbor,
        ).inc()

    def __parse_ospf_neighbor(self, msg):
        error = msg["error"]
        if error not in self.metrics:
            self.metrics[error] = Counter(
                "napalm_logs_{error}".format(error=error.lower()),
                "Counter for {error} notifications".format(error=error),
                ["host", "area", "neighbor", "interface"],
            )
        if "ospf_neighbor" not in self.metrics:
            self.metrics["ospf_neighbor"] = Gauge(
                "napalm_logs_ospf_neighbor_state",
                "State of the OSPF neighbor. 0=DOWN, 1=UP",
                ["host", "area", "neighbor", "interface"],
            )
        area_dict = msg["yang_message"]["network-instances"]["network-instance"][
            "global"
        ]["protocols"]["protocol"]["ospf"]["ospfv2"]["areas"]["area"]
        area_id = list(area_dict.keys())[0]
        iface_dict = area_dict[area_id]["interfaces"]["interface"]
        iface_name = list(iface_dict.keys())[0]
        neighbor = list(iface_dict[iface_name]["neighbors"]["neighbor"].keys())[0]
        labels = {
            "host": msg["host"],
            "area": area_id,
            "neighbor": neighbor,
            "interface": iface_name,
        }
        self.metrics[error].labels(**labels).inc()
        state = 1 if error == "OSPF_NEIGHBOR_UP" else 0
        self.metrics["ospf_neighbor"].labels(**labels).set(state)

    def __parse_isis_neighbor(self, msg):
        error = msg["error"]
        if error not in self.metrics:
            self.metrics[error] = Counter(
                "napalm_logs_{error}".format(error=error.lower()),
                "Counter for {error} notifications".format(error=error),
                ["host", "interface", "level", "neighbor"],
            )
        if "isis_neighbor" not in self.metrics:
            self.metrics["isis_neighbor"] = Gauge(
                "napalm_logs_isis_neighbor_state",
                "State of the ISIS neighbor. 0=DOWN, 1=UP",
                ["host", "interface", "level", "neighbor"],
            )
        iface_dict = msg["yang_message"]["network-instances"]["network-instance"][
            "global"
        ]["protocols"]["protocol"]["isis"]["interfaces"]["interface"]
        iface_name = list(iface_dict.keys())[0]
        level_dict = iface_dict[iface_name]["levels"]["level"]
        level = list(level_dict.keys())[0]
        neighbor = list(level_dict[level]["adjacencies"]["adjacency"].keys())[0]
        labels = {
            "host": msg["host"],
            "interface": iface_name,
            "level": level,
            "neighbor": neighbor,
        }
        self.metrics[error].labels(**labels).inc()
        state = 1 if error == "ISIS_NEIGHBOR_UP" else 0
        self.metrics["isis_neighbor"].labels(**labels).set(state)

    def __parse_nat_session(self, msg):
        error = msg["error"]
        labels = [
            "service_name",
            "source_address",
            "source_port",
            "destination_address",
            "destination_port",
            "nat_destination_address",
            "nat_destination_port",
            "nat_source_address",
            "nat_source_port",
        ]
        if error not in self.metrics:
            self.metrics[error] = Counter(
                "napalm_logs_{error}".format(error=error.lower()),
                "Counter for {error} notifications".format(error=error),
                ["host"] + labels,
            )
        event = list(msg["yang_message"]["security"]["flow"].keys())[0]
        label_values = {"host": msg["host"]}
        for label in labels:
            label_values[label] = msg["yang_message"]["security"]["flow"][event][label]
        self.metrics[error].labels(**label_values).inc()

    def _parse_interface_down(self, msg):
        """
        Build metrics from INTERFACE_DOWN notifications.
        """
        self.__parse_interface_basic(msg)

    def _parse_interface_up(self, msg):
        """
        Build metrics from INTERFACE_UP notifications.
        """
        self.__parse_interface_basic(msg)

    def _parse_interface_duplex_mode(self, msg):
        """
        Build metrics from INTERFACE_DUPLEX_MODE notifications.
        """
        if "INTERFACE_DUPLEX_MODE" not in self.metrics:
            self.metrics["INTERFACE_DUPLEX_MODE"] = Counter(
                "napalm_logs_interface_duplex_mode",
                "Counter for INTERFACE_DUPLEX_MODE notifications",
                ["host", "interface", "duplex_mode"],
            )
        iface_dict = msg["yang_message"]["interfaces"]["interface"]
        iface_name = list(iface_dict.keys())[0]
        self.metrics["INTERFACE_DUPLEX_MODE"].labels(
            host=msg["host"],
            interface=iface_name,
            duplex_mode=iface_dict[iface_name]["ethernet"]["state"]["duplex_mode"],
        )

    def _parse_interface_mac_limit_reached(self, msg):
        """
        Build metrics from INTERFACE_MAC_LIMIT_REACHED notifications.
        """
        if "INTERFACE_MAC_LIMIT_REACHED" not in self.metrics:
            self.metrics["INTERFACE_MAC_LIMIT_REACHED"] = Gauge(
                "napalm_logs_interface_mac_limit_reached",
                "Counter for INTERFACE_MAC_LIMIT_REACHED notifications",
                ["host", "interface"],
            )
        iface_dict = msg["yang_message"]["interfaces"]["interface"]
        iface_name = list(iface_dict.keys())[0]
        self.metrics["INTERFACE_MAC_LIMIT_REACHED"].labels(
            host=msg["host"], interface=iface_name
        ).set(iface_dict[iface_name]["ethernet"]["state"]["learned-mac-addresses"])

    def _parse_lacp_interface_down(self, msg):
        """
        Build metrics for LACP_INTERFACE_DOWN messages.
        """
        self.__parse_lacp(msg)

    def _parse_bfd_state_change(self, msg):
        """
        Build metrics from BFD_STATE_CHANGE.
        """
        if "BFD_STATE_CHANGE" not in self.metrics:
            self.metrics["BFD_STATE_CHANGE"] = Counter(
                "napalm_logs_bfd_state_change",
                "Counter for BFD_STATE_CHANGE notifications",
                ["host", "interface", "session_state"],
            )
        iface_dict = msg["yang_message"]["bfd"]["interfaces"]["interface"]
        self.metrics["BFD_STATE_CHANGE"].labels(
            host=msg["host"],
            interface=iface_dict["id"],
            session_state=iface_dict["peers"]["peer"]["state"]["session-state"],
        ).inc()

    def _parse_ntp_server_unreachable(self, msg):
        """
        Build metrics from NTP_SERVER_UNREACHABLE notifications.
        """
        if "NTP_SERVER_UNREACHABLE" not in self.metrics:
            self.metrics["NTP_SERVER_UNREACHABLE"] = Counter(
                "napalm_logs_ntp_server_unreachable",
                "Counter for NTP_SERVER_UNREACHABLE notifications",
                ["host", "ntp_server"],
            )
        self.metrics["NTP_SERVER_UNREACHABLE"].labels(
            host=msg["host"],
            ntp_server=list(
                msg["yang_message"]["system"]["ntp"]["servers"]["server"].keys()
            )[0],
        ).inc()

    def _parse_bgp_prefix_limit_exceeded(self, msg):
        """
        Build metrics form BGP_PREFIX_LIMIT_EXCEEDED notifications.
        """
        self.__parse_bgp_basic(msg)

    def _parse_bgp_prefix_thresh_exceeded(self, msg):
        """
        Build metrics from BGP_PREFIX_THRESH_EXCEEDED notifications.
        """
        self.__parse_bgp_basic(msg)

    def _parse_bgp_peer_not_configured(self, msg):
        """
        Build metrics from BGP_PEER_NOT_CONFIGURED notifications.
        """
        self.__parse_bgp_basic(msg)

    def _parse_bgp_session_not_configured(self, msg):
        """
        Build metrics from BGP_SESSION_NOT_CONFIGURED notifications.
        """
        self.__parse_bgp_no_asn(msg)

    def _parse_bgp_connection_rejected(self, msg):
        """
        Build metrics from BGP_CONNECTION_REJECTED notifications.
        """
        self.__parse_bgp_basic(msg)

    def _parse_bgp_connection_reset(self, msg):
        """
        Build metrics from BGP_CONNECTION_RESET notifications.
        """
        self.__parse_bgp_basic(msg)

    def _parse_bgp_incorrect_as_number(self, msg):
        """
        Build metrics from BGP_INCORRECT_AS_NUMBER notifications.
        """
        self.__parse_bgp_basic(msg)

    def _parse_bgp_neighbor_state_changed(self, msg):
        """
        Build metrics from BGP_NEIGHBOR_STATE_CHANGED.
        """
        self.__parse_bgp_basic(msg)

    def _parse_bgp_md5_incorrect(self, msg):
        """
        Build metrics from BGP_MD5_INCORRECT.
        """
        self.__parse_bgp_no_asn(msg)

    def _parse_bgp_cease_prefix_limit_exceeded(self, msg):
        """
        Build metrics for BGP_CEASE_PREFIX_LIMIT_EXCEEDED.
        """
        self.__parse_network_instance_bgp(msg)

    def _parse_user_enter_config_mode(self, msg):
        """
        Build metrics for USER_ENTER_CONFIG_MODE.
        """
        self.__parse_user_action(msg)

    def _parse_user_exit_config_mode(self, msg):
        """
        Build metrics for USER_EXIT_CONFIG_MODE.
        """
        self.__parse_user_action(msg)

    def _parse_user_write_config(self, msg):
        """
        Build metrics for USER_WRITE_CONFIG.
        """
        self.__parse_user_action(msg)

    def _parse_user_login(self, msg):
        """
        Build metrics for USER_LOGIN.
        """
        self.__parse_user_action(msg)

    def _parse_user_logout(self, msg):
        """
        Build metrics for USER_LOGOUT.
        """
        self.__parse_user_action(msg)

    def _parse_configuration_commit_requested(self, msg):
        """
        Build metrics for CONFIGURATION_COMMIT_REQUESTED.
        """
        self.__parse_user_action(msg)

    def _parse_configuration_rollback(self, msg):
        """
        Build metrics for CONFIGURATION_ROLLBACK.
        """
        self.__parse_user_action(msg)

    def _parse_system_alarm(self, msg):
        """
        Build metrics for SYSTEM_ALARM.
        """
        error = msg["error"]
        if error not in self.metrics:
            self.metrics[error] = Counter(
                "napalm_logs_{error}".format(error=error.lower()),
                "Counter for {error} notifications".format(error=error),
                [
                    "host",
                    "component_name",
                    "component_class",
                    "alarm_state",
                    "alarm_reason",
                ],
            )
        if "system_alarm_state" not in self.metrics:
            self.metrics["system_alarm_state"] = Gauge(
                "napalm_logs_system_alarm_state",
                "State of the system alarm. 1=SET, 0=CLEARED",
                [
                    "host",
                    "component_name",
                    "component_class",
                    "alarm_state",
                    "alarm_reason",
                ],
            )
        component = msg["yang_message"]["hardware-state"]["component"]
        component_name = list(component.keys())[0]
        labels = {
            "host": msg["host"],
            "component_name": component_name,
            "component_class": component[component_name]["class"],
            "alarm_state": component[component_name]["state"]["alarm-state"],
            "alarm_reason": component[component_name]["state"]["alarm-reason"],
        }
        self.metrics[error].labels(**labels).inc()
        state = 1 if error == "SYSTEM_ALARM" else 0
        self.metrics["system_alarm_state"].labels(**labels).set(state)

    def _parse_system_alarm_cleared(self, msg):
        return self._parse_system_alarm(msg)

    def __parse_minor_major_alarm(self, msg):
        """
        Build metrics for MINOR_ALARM_* and MAJOR_ALARM_* notifications.
        """
        error = msg["error"]
        if error not in self.metrics:
            self.metrics[error] = Counter(
                "napalm_logs_{error}".format(error=error.lower()),
                "Counter for {error} notifications".format(error=error),
                ["host", "alarm_reason"],
            )
        severity = error.split("_")[0].lower()
        alarm_state_metric = "{}_alarm_state".format(severity)
        if alarm_state_metric not in self.metrics:
            self.metrics[alarm_state_metric] = Gauge(
                "napalm_logs_{}".format(alarm_state_metric),
                "State of the {} system alarm. 1=SET, 0=CLEARED".format(severity),
                ["host", "alarm_reason"],
            )
        labels = {
            "host": msg["host"],
            "alarm_reason": msg["yang_message"]["alarms"]["alarm"]["additional-text"],
        }
        self.metrics[error].labels(**labels).inc()
        state = 1 if error == "{}_ALARM_SET".format(severity.upper()) else 0
        self.metrics[alarm_state_metric].labels(**labels).set(state)

    def _parse_major_alarm_set(self, msg):
        return self.__parse_minor_major_alarm(msg)

    def _parse_major_alarm_cleared(self, msg):
        return self.__parse_minor_major_alarm(msg)

    def _parse_minor_alarm_set(self, msg):
        return self.__parse_minor_major_alarm(msg)

    def _parse_minor_alarm_cleared(self, msg):
        return self.__parse_minor_major_alarm(msg)

    def _parse_ospf_neighbor_up(self, msg):
        """
        Build metrics for OSPF_NEIGHBOR_UP.
        """
        self.__parse_ospf_neighbor(msg)

    def _parse_ospf_neighbor_down(self, msg):
        """
        Build metrics for OSPF_NEIGHBOR_DOWN.
        """
        self.__parse_ospf_neighbor(msg)

    def _parse_isis_neighbor_up(self, msg):
        """
        Build metrics for ISIS_NEIGHBOR_UP.
        """
        self.__parse_isis_neighbor(msg)

    def _parse_isis_neighbor_down(self, msg):
        """
        Build metrics for ISIS_NEIGHBOR_DOWN.
        """
        self.__parse_isis_neighbor(msg)

    def _parse_nat_session_created(self, msg):
        """
        Build metrics for NAT_SESSION_CREATED.
        """
        self.__parse_nat_session(msg)

    def _parse_nat_session_closed(self, msg):
        """
        Build metrics for NAT_SESSION_CLOSED.
        """
        self.__parse_nat_session(msg)

    def _parse_ddos_protocol_violation_set(self, msg):
        """
        Build metrics for DDOS_PROTOCOL_VIOLATION_SET messages.
        """
        error = msg["error"]
        if error not in self.metrics:
            self.metrics[error] = Counter(
                "napalm_logs_{error}".format(error=error.lower()),
                "Counter for {error} notifications".format(error=error),
                ["host", "event_type", "entity_type", "additional_text"],
            )
        alarm_dict = msg["yang_message"]["alarms"]["alarm"]
        labels = {
            "host": msg["host"],
            "event_type": alarm_dict["event-type"],
            "entity_type": alarm_dict["entity-type"],
            "additional_text": alarm_dict["additional-text"],
        }
        self.metrics[error].labels(**labels).inc()

    def start(self):
        log.debug("Starting the Prometheus publisher")

    def publish(self, obj):
        data = napalm_logs.utils.unserialize(obj)
        if data["error"] in ("RAW", "UNKNOWN"):
            return
        fun_name = "_parse_{}".format(data["error"].lower())
        if hasattr(self, fun_name):
            try:
                getattr(self, fun_name)(data)
            except Exception:
                log.error(data, exc_info=True)
                raise
        else:
            # Anything else goes into __parse_without_details which generates
            # metrics using the napalm-logs error name, and the host as the only
            # label. If we want something more specific than that, e.g., more
            # (specific) labels, we'll define a _parse function as above.
            self.__parse_without_details(data)

    def stop(self):
        log.debug("Stopping the Prometheus publisher")
