### idapro95-docker

[![Docker Pulls](https://img.shields.io/docker/pulls/stackoverflowexcept1on/idapro)](https://hub.docker.com/r/stackoverflowexcept1on/idapro)
[![Docker Image CLI](https://img.shields.io/badge/docker_image_(9.5_cli)-~1.77GB-blue)](https://hub.docker.com/r/stackoverflowexcept1on/idapro)
[![Docker Image X11](https://img.shields.io/badge/docker_image_(9.5_x11)-~1.98GB-blue)](https://hub.docker.com/r/stackoverflowexcept1on/idapro)

IDA Pro 9.5 Beta 1 Docker Image that can be used both in batch mode (without GUI) and with X11 forwarding. You can run IDA Pro on a Linux server at night and get `database.i64` the next day.

### Requirements

- `ida-pro_95_armlinux.run` & `ida-pro_95_x64linux.run` files, which can be downloaded from release page

### Platform detection

```bash
PLATFORM=$(case "$(uname -m)" in
  aarch64) echo linux/arm64 ;;
  x86_64) echo linux/amd64 ;;
esac)
```

### Building

```bash
docker build \
    --build-arg MODE=cli \
    --platform "$PLATFORM" \
    --tag stackoverflowexcept1on/idapro:9.5-cli .
```

```bash
docker build \
    --build-arg MODE=x11 \
    --platform "$PLATFORM" \
    --tag stackoverflowexcept1on/idapro:9.5-x11 .
```

### Installing

If you don't want to build anything, pre-built docker image is available:

```bash
docker pull \
    --platform "$PLATFORM" \
    stackoverflowexcept1on/idapro:9.5-cli
```

```bash
docker pull \
    --platform "$PLATFORM" \
    stackoverflowexcept1on/idapro:9.5-x11
```

### Running

```bash
mkdir -p demo && cd demo
cp /bin/cat .
docker run \
    --hostname hostname \
    --interactive \
    --name container \
    --platform "$PLATFORM" \
    --rm \
    --tty \
    --volume "$(pwd)":/files \
    stackoverflowexcept1on/idapro:9.5-cli \
        -B \
        -P+ \
        /files/cat
ls cat.i64
```

```bash
mkdir -p demo && cd demo
cp /bin/cat .
xhost +local:docker
docker run \
    --hostname hostname \
    --interactive \
    --env DISPLAY=$DISPLAY \
    --name container \
    --platform "$PLATFORM" \
    --rm \
    --tty \
    --volume "$(pwd)":/files \
    --volume /tmp/.X11-unix:/tmp/.X11-unix \
    stackoverflowexcept1on/idapro:9.5-x11 \
        /files/cat
ls cat.i64
```
