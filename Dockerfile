FROM ubuntu:25.10 AS builder
RUN apt update && \
    apt install --no-install-recommends --yes \
        python3 \
        libpython3.13 && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /opt/ida-pro-9.2
COPY . /opt/ida-pro-9.2
RUN echo "485485dda6faf88c23732105400a2a60279e755b1a032aea52900c1333cf0351 ida-pro_92_x64linux.run" | sha256sum -c && \
    chmod +x ida-pro_92_x64linux.run && \
    mkdir -p /root/.local/share/applications && \
    ./ida-pro_92_x64linux.run --mode unattended --prefix /opt/ida-pro-9.2 && \
    rm ida-pro_92_x64linux.run && \
    ./idapyswitch --verbose --auto-apply --ignore-python-config && \
    export PYTHONDONTWRITEBYTECODE=1 && \
    python3 idakeygen.py && \
    python3 idareggen.py && \
    rm idakeygen.py && \
    rm idareggen.py && \
    sed -i '37,46d' idc/analysis.idc

FROM ubuntu:25.10
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
WORKDIR /opt/ida-pro-9.2
COPY --from=builder /opt/ida-pro-9.2 /opt/ida-pro-9.2
COPY --from=builder /root/.idapro /root/.idapro
ENTRYPOINT ["/opt/ida-pro-9.2/entrypoint.sh"]
