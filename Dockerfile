FROM ubuntu:26.04 AS builder
RUN apt update && \
    apt install --no-install-recommends --yes \
        python3 \
        libpython3.14 && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /opt/ida-pro-9.4
COPY . /opt/ida-pro-9.4
RUN IDA_RUN=$(case "$(uname -m)" in \
        aarch64) echo ida-pro_94_armlinux.run ;; \
        x86_64) echo ida-pro_94_x64linux.run ;; \
    esac) && \
    IDA_CHECKSUM=$(case "$(uname -m)" in \
        aarch64) echo edafadd057c92153fd25a3f46a0b4581b1e052d415d1762891e9b78831a04abe ;; \
        x86_64) echo eabb64c3c849d3858759558359e9cebcf17e2a91bcc60523533df8b84462aa54 ;; \
    esac) && \
    echo "$IDA_CHECKSUM $IDA_RUN" | sha256sum -c && \
    chmod +x "$IDA_RUN" && \
    mkdir -p /root/.local/share/applications && \
    "./$IDA_RUN" --mode unattended && \
    rm "$IDA_RUN" && \
    ./idapyswitch --verbose --auto-apply --ignore-python-config && \
    export PYTHONDONTWRITEBYTECODE=1 && \
    python3 idakeygen.py --oneshot && \
    python3 idareggen.py && \
    rm idakeygen.py && \
    rm idareggen.py && \
    rm libida.so.bak && \
    rm libida32.so.bak && \
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
            libxkbcommon-x11-0 \
            libxtst6; \
    fi && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /opt/ida-pro-9.4
COPY --from=builder /opt/ida-pro-9.4 /opt/ida-pro-9.4
COPY --from=builder /root/.idapro /root/.idapro
ENTRYPOINT ["/opt/ida-pro-9.4/entrypoint.sh"]
