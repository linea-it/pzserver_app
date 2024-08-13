#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

echo "Starting Celery Beat"

rm -rf /tmp/celerybeat.pid

celery -A pzserver beat \
    -l "${LOGGING_LEVEL}" \
    -s /tmp/celerybeat-schedule \
    --pidfile="/tmp/celerybeat.pid" \
    --logfile="/archive/log/celerybeat.log" 