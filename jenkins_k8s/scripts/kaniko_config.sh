#!/bin/bash

DOCKER_USERNAME=$1
DOCKER_PASSWORD=$2
AUTH=$(echo -n "${DOCKER_USERNAME}:${DOCKER_PASSWORD}" | base64 -w 0)
cat << EOF > config.json
{
    "auths": {
        "https://scribesecuriy.jfrog.io": {
            "auth": "${AUTH}"
        }
    }
}
EOF
