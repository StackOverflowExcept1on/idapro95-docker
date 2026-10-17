#!/usr/bin/env sh
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
export IDA_NO_RELEASE_NOTES=1

if [ "$MODE" = "cli" ]; then
    exec /opt/ida-pro-9.5/idat "$@"
elif [ "$MODE" = "x11" ]; then
    exec /opt/ida-pro-9.5/ida "$@"
else
    exit 1
fi
