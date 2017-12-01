# Docker support for Napalm-logs
The files in this directory help facilitate deploying a containerized version of Napalm-logs using Docker.

The default configuration will allow you to publish to Kafka. If you wish to change this, clone the repository and edit the `Dockerfile` and `napalm.tmpl` files.


## Usage
- The default configuration will publish messages to a Kafka broker located at `127.0.0.1:9092` to a topic `syslog.net`.
- The container will map internal port 514 to port 514 on the host and listen for incoming messages.
   - You can change the port which Docker maps to the internal 514 port at container runtime.
   - This provides an easy way to change what port incoming messages are received on.

[A pre-built Docker image is also available on Docker Hub.](https://hub.docker.com/r/nathancatania/napalm-logs/)
Security is disabled by default in the pre-built image. As such, it is recommended for testing use only; not deployment in production.

### Customize your configuration
- The `napalm.tmpl` file is rendered at container runtime and used as the configuration file.
- All required changes to the configuration should go into this file.
- Any options specified inside `{{ }}` can be dynamically set using ENV variables either within the Dockerfile, or by specifying the `-e` variable at container runtime.
- If you require additonal files to be added to the Docker container (eg: Certificate files), you can add in additional `COPY` commands within the Dockerfile.

### Build the image
1. Navigate to the directory containing the Dockerfile.
2. Execute:
```
docker build napalm-logs:latest .
```
This will build the image tagged as `napalm-logs:latest`.

### Run the image
To run the image with the default configuration:
```
docker run -d -p 514:514/udp napalm-logs:latest
```
- This will deploy a single container instance and begin listening for incoming messages on port 514 of the host.
- The default configuration specifies a Kafka broker running on `127.0.0.1` on port 9092, with all data being published to the `syslog.net` topic.
- You can change these defaults by specifying ENV variables at runtime. See the __Variables__ section below.

### Using the pre-built image
[A pre-built Docker image is also available on Docker Hub.](https://hub.docker.com/r/nathancatania/napalm-logs/)

Usage:
```
docker run -d -p 514:514/udp -i nathancatania/napalm-logs:latest
```
The pre-built image allows the variables specified in the __Variables__ section below to be altered.


## Variables
By default, the container listens to UDP traffic on port 514 and will push it to a Kafka broker running on `localhost:9092`.

You can change this by overwriting the ENV variables when launching the container. A list of available variables (and their defaults) is below.
```yaml
PUBLISH_PORT: 49017              # Port to publish data to Kafka on
KAFKA_BROKER_HOST: 127.0.0.1     # Hostname or IP of the Kafka broker to publish to
KAFKA_BROKER_PORT: 9092          # Port of the Kafka broker to publish to
KAFKA_TOPIC: syslog.net          # The Kafka topic to push data to.
SEND_RAW: true                   # Publish messages where the OS, but NOT the message could be identified.
SEND_UNKNOWN: false              # Publish messages where both OS and message could not be identified.
WORKER_PROCESSES: 1              # Increasing this increases memory consumption but is better for higher loads.
```
If you want to change the port that the container listens on to receive Syslog data, you can alter the port mapping on container launch.

Example (changing the ENV variables and port mapping):
```
docker run -d -e KAFKA_BROKER_HOST=192.168.1.200 -e KAFKA_TOPIC=my_topic -p 6000:514/udp -i napalm-logs:latest
```
In this example:
- Internally the container is still listening on port 514, however Docker will map this to external port 6000 on the host. As the user, you will direct your Syslog traffic to port 6000.
- Napalm-logs will connect to a Kafka broker located at `192.168.1.200`.
- As the `KAFKA_BROKER_PORT` variable was NOT included, the default port of 9092 will be used for the Kafka broker connection.
- Data will be published to the Kafka topic `my_topic`.


## Security
The default configuration will execute napalm-logs with the `--disable-security option` enabled.
Do __NOT__ use this for production. Consult the [napalm-logs documentation](http://napalm-logs.readthedocs.io/en/latest/authentication/index.html) on how to add a certificate & keyfile.

## Altering the Configuration
If you don't want to output to Kafka, you can change the configuration in the napalm.tmpl file. This file is rendered when the container starts based on the ENV variables defined in the Dockerfile (or those specified at runtime).
