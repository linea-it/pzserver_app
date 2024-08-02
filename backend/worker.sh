#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

host=$(hostname)

sleep 5

echo "Starting Celery Worker"

rm -rf /tmp/local-*.pid

celery -A pzserver worker \
    -l "${LOGGING_LEVEL}" \
    --pidfile="/tmp/local-%n.pid" \
    --logfile="/archive/log/${host}%I.log" \
    --concurrency=2