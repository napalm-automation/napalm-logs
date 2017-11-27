FROM alpine:3.6
MAINTAINER Nathan Catania <nathan@nathancatania.com>

ENV NAPALM_LOGS_DOCKER_VERSION 0.3.0

# Copy script to generate Napalm-logs configuration dynamically
ADD     startnapalm.sh /usr/bin/startnapalm.sh
COPY    napalm.tmpl /usr/bin/napalm.tmpl

# Install napalm-logs and pre-requisites
RUN apk add --no-cache \
    libffi \
    libffi-dev \
    python \
    python-dev \
    py-pip \
    build-base \
    && pip install envtpl \
    && pip install cffi \
    && pip install kafka \
    && pip install napalm-logs \
    && chmod 777 /usr/bin/startnapalm.sh \
    && mkdir -p /tmp/napalm-logs

EXPOSE 514/udp

# Default configuration to be rendered
ENV PUBLISH_PORT=49017 \
    KAFKA_BROKER_HOST=127.0.0.1 \
    KAFKA_BROKER_PORT=9092 \
    KAFKA_TOPIC=syslog.net \
    SEND_UNKNOWN=false \
    SEND_RAW=true \
    WORKER_PROCESSES=1

CMD /usr/bin/startnapalm.sh
