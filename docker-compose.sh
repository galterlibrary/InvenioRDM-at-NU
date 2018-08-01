#!/bin/bash

# This script performs the 2 stage build and runs docker-compose.

# Arguments
#   <GITHUB_PRIVATE_TOKEN>
#   <docker-compose file to use: docker-compose.ci.yml OR docker-compose.prod.yml>

if [[ "$#" -lt 2 ]]; then
    echo "USAGE: docker-compose.sh <GITHUB_PRIVATE_TOKEN> <docker-compose.ci.yml | docker-compose.prod.yml>"
    exit 1
fi

GITHUB_PRIVATE_TOKEN="$1"
DOCKER_COMPOSE_FILE="$2"

# Builder image
docker build --build-arg GITHUB_PRIVATE_TOKEN=$GITHUB_PRIVATE_TOKEN --tag cd2h-repo-builder-image --file Dockerfile.builder .
docker create --name cd2h-repo-builder cd2h-repo-builder-image
PWD=`pwd`
sudo su -c "docker cp cd2h-repo-builder:/usr/local/lib/python3.5/site-packages/. $PWD/docker/build/site-packages"
sudo su -c "docker cp cd2h-repo-builder:/usr/local/bin/. $PWD/docker/build/bin"

# Cleanup
docker rm cd2h-repo-builder

docker-compose --file $DOCKER_COMPOSE_FILE up --build --detach
