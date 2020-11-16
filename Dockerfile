FROM python:3.6-alpine

COPY docker/config.txt /etc/napalm/logs
COPY ./ /var/cache/napalm-logs/

# Install napalm-logs and pre-requisites
RUN apk add --no-cache \
    libffi \
    libffi-dev \
    python3-dev \
    build-base \
    && pip --no-cache-dir install cffi pyzmq==19.0.2 /var/cache/napalm-logs/ \
    && rm -rf /var/cache/napalm-logs/

CMD napalm-logs --config-file /etc/napalm/logs
