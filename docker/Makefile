NAME := napalm_logs
# This can be changed to build with different BUILD_REQS
VERSION ?= $(shell git describe --tags $(git rev-list --tags --max-count=1))

## To specify which dependencies to install please set BUILD_REQS
## For example:
## make BUILD_REQS="kafka tornado" build

IMAGE = $(NAME):$(VERSION)
REPO ?= mirceaulinic/napalm-logs

DOCKERFILE ?= Dockerfile
DOCKER_BUILD_CONTEXT ?= $(dir $(abspath $(PWD)../))

.PHONY: build
build: clean
	docker build -f ../$(DOCKERFILE) -t $(IMAGE) $(DOCKER_BUILD_CONTEXT) --build-arg requirements="${BUILD_REQS}"

.PHONY: publish
publish: build
	docker tag $(IMAGE) $(REPO):$(VERSION)
	echo "$(DOCKER_PASSWORD)" | docker login -u "$(DOCKER_USERNAME)" --password-stdin
	docker push $(REPO):$(VERSION)

PORTS:=$(shell grep port config.txt | sed 's/[^0-9]*//g') 
PORT_MAP:=$(foreach port,$(PORTS),-p $(port):$(port)/udp -p $(port):$(port))

.PHONY: run
run: clean
	docker run -d -v $(shell pwd)/config.txt:/tmp/napalm-logs/config.txt --name $(NAME) --hostname $(NAME) ${PORT_MAP} $(IMAGE)

.PHONY: run-foreground
run-foreground: clean
	docker run -t -i -v $(shell pwd)/config.txt:/tmp/napalm-logs/config.txt --name $(NAME) --hostname $(NAME) ${PORT_MAP} $(IMAGE)

.PHONY: clean
clean:
	docker rm -f $(NAME) || true
