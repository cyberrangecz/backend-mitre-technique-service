#!/usr/bin/env sh

LISTEN_IP=0.0.0.0
LISTEN_PORT=8001
GUNICORN_WORKER_TIMEOUT=60

set -e

gunicorn crczp.mitre_technique_project.wsgi:application --bind ${LISTEN_IP}:${LISTEN_PORT} --timeout ${GUNICORN_WORKER_TIMEOUT}
