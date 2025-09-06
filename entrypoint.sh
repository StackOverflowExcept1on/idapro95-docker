#!/usr/bin/env sh
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

if [ "$MODE" = "cli" ]; then
    exec /opt/ida-pro-9.2/idat "$@"
elif [ "$MODE" = "x11" ]; then
    exec /opt/ida-pro-9.2/ida "$@"
else
    exit 1
fi
