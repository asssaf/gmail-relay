#!/usr/bin/env bash

set +e

: ${IMAGE="asssaf/gmail-relay"}

# mount current dir on host to attach dir so it can be accessed for attachment files
MOUNT="$PWD"

docker run --rm \
	-v $MOUNT:/attach:ro \
	--entrypoint=/create-message.py \
        $IMAGE "$@"
