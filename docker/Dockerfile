FROM alpine:3.6

ARG requirements=""
ARG version=""

RUN mkdir /etc/napalm
COPY config.txt /etc/napalm/logs

# Install napalm-logs and pre-requisites
RUN apk add --no-cache \
    libffi \
    libffi-dev \
    python \
    python-dev \
    py-pip \
    build-base \
    && pip install cffi \
    && pip install napalm-logs==$version

RUN for req in $requirements; do \
        pip install $req; \
    done

CMD napalm-logs --config-file /etc/napalm/logs
