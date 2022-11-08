FROM python:3.9-slim-buster

COPY docker/config.txt /etc/napalm/logs
COPY ./ /var/cache/napalm-logs/

# Install napalm-logs and pre-requisites
RUN apt-get update \
 && apt-get install -y dumb-init python3-dev python3-cffi libffi-dev \
 && pip --no-cache-dir install -U pip \
 && pip --no-cache-dir install /var/cache/napalm-logs/ \
 && rm -rf /var/cache/napalm-logs/

ENTRYPOINT ["/usr/bin/dumb-init", "--"]

CMD ["napalm-logs", "--config-file", "/etc/napalm/logs"]
