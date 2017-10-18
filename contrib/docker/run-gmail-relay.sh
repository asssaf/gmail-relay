#!/usr/bin/env bash

set +e

: ${IMAGE="asssaf/gmail-relay"}
: ${CONFIG_DIR="$HOME/.config/gmail-relay"}

[ -d "$CONFIG_DIR" ] || mkdir -p $CONFIG_DIR

docker run --rm -i \
	-v $CONFIG_DIR:/config \
	--entrypoint=/gmail-relay.py \
        $IMAGE --config /config --noauth_local_webserver "$@"
