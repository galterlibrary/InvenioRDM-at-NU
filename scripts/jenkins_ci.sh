#!/usr/bin/env bash
# This script runs the continuous integration tests on Jenkins and makes
# sure a non-zero exit code is returned if the test service fails.
#
# A whole script is necessary, because docker-compose is returning a zero exit
# code even if there is a non-zero exiting service. This bug has been reported
# here: https://github.com/docker/compose/issues/6776
set -ex

cleanup() {
    rm -f $TMP
}

trap cleanup EXIT

TMP=$(mktemp CI-XXXXXXXXXX)
SERVICE=app
docker-compose --file docker-compose.ci.yml up --build --no-color --exit-code-from $SERVICE | tee $TMP
grep -q "_${SERVICE}_1 exited with code 0" $TMP
