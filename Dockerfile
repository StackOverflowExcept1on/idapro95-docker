FROM ubuntu:26.04 AS builder
RUN apt update && \
    apt install --no-install-recommends --yes \
        python3 \
        libpython3.14 && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /opt/ida-pro-9.3
COPY . /opt/ida-pro-9.3
RUN IDA_RUN=$(case "$(uname -m)" in \
        aarch64) echo ida-pro_93_armlinux.run ;; \
        x86_64) echo ida-pro_93_x64linux.run ;; \
    esac) && \
    IDA_CHECKSUM=$(case "$(uname -m)" in \
        aarch64) echo 2ca611571c39c2f164b6ac8e6e7500088018b1755dbaf6796e538cb43a4ea10b ;; \
        x86_64) echo a64e6589feeca0f4e1bfb962d1a283761fb38c5158f5f82c8f1e7ddf32f69850 ;; \
    esac) && \
    echo "$IDA_CHECKSUM $IDA_RUN" | sha256sum -c && \
    chmod +x "$IDA_RUN" && \
    mkdir -p /root/.local/share/applications && \
    "./$IDA_RUN" --mode unattended && \
    rm "$IDA_RUN" && \
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
        libpython3.14 && \
    if [ "$MODE" = "x11" ]; then \
        apt install --no-install-recommends --yes \
            libdbus-1-3 \
            libegl1 \
            libfontconfig1 \
            libgl1 \
            libglib2.0-0 \
            libopengl0 \
            libsecret-1-0 \
            libsm6 \
            libxcb-cursor0 \
            libxcb-icccm4 \
            libxcb-image0 \
            libxcb-keysyms1 \
            libxcb-render-util0 \
            libxcb-shape0 \
            libxcb-xinerama0 \
            libxcb-xkb1 \
            libxkbcommon-x11-0; \
    fi && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /opt/ida-pro-9.3
COPY --from=builder /opt/ida-pro-9.3 /opt/ida-pro-9.3
COPY --from=builder /root/.idapro /root/.idapro
ENTRYPOINT ["/opt/ida-pro-9.3/entrypoint.sh"]
