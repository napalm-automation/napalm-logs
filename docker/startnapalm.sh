#!/bin/sh
envtpl --keep-template /usr/bin/napalm.tmpl -o /tmp/napalm-logs/napalm.conf
napalm-logs --config-file /tmp/napalm-logs/napalm.conf
