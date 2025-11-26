#!/usr/bin/env bash
set -euo pipefail

UVICORN_CMD=${UVICORN_CMD:-uvicorn}
APP_PATH=${APP_PATH:-server.main:app}
PORT=${PORT:-8000}

exec ${UVICORN_CMD} ${APP_PATH} --host 0.0.0.0 --port ${PORT}
