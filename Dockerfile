FROM ubuntu:26.04 AS builder
RUN apt update && \
    apt install --no-install-recommends --yes \
        python3 \
        libpython3.13 && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /opt/ida-pro-9.3
COPY . /opt/ida-pro-9.3
RUN echo "2ed43ae4bb84d74dcae6f0099210dfa8d61bfea4952f5f9a07a9aae16cb70f82 ida-pro_93_x64linux.run" | sha256sum -c && \
    chmod +x ida-pro_93_x64linux.run && \
    mkdir -p /root/.local/share/applications && \
    ./ida-pro_93_x64linux.run --mode unattended && \
    rm ida-pro_93_x64linux.run && \
    ./idapyswitch --verbose --auto-apply --ignore-python-config && \
    export PYTHONDONTWRITEBYTECODE=1 && \
    python3 idakeygen.py && \
    python3 idareggen.py && \
    rm idakeygen.py && \
    rm idareggen.py && \
    sed -i '37,46d' idc/analysis.idc

FROM ubuntu:26.04
ARG MODE=cli
ENV MODE=$MODE
RUN apt update && \
    apt install --no-install-recommends --yes \
        python3 \
        libpython3.13 && \
    if [ "$MODE" = "x11" ]; then \
        apt install --no-install-recommends --yes \
            libgl1 \
            libopengl0 \
            libegl1 \
            libglib2.0-0 \
            libfontconfig1 \
            libxcb-cursor0 \
            libxcb-icccm4 \
            libxcb-image0 \
            libxcb-keysyms1 \
            libxcb-render-util0 \
            libxcb-shape0 \
            libxcb-xinerama0 \
            libxcb-xkb1 \
            libsm6 \
            libxkbcommon-x11-0 \
            libdbus-1-3; \
    fi && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /opt/ida-pro-9.3
COPY --from=builder /opt/ida-pro-9.3 /opt/ida-pro-9.3
COPY --from=builder /root/.idapro /root/.idapro
ENTRYPOINT ["/opt/ida-pro-9.3/entrypoint.sh"]
