FROM alpine:3.6

ARG requirements=""
ARG version=""

WORKDIR /tmp/napalm-logs
COPY config.txt .

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

CMD napalm-logs --config-file config.txt
