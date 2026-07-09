#!/usr/bin/env bash
set -Eeuo pipefail

# Run Alembic migrations against the configured production database.
# This script sources backend/.env.production by default. Keep secrets only on the server.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
VENV_DIR="${VENV_DIR:-$ROOT_DIR/.venv}"
ENV_FILE="${BACKEND_ENV_FILE:-$BACKEND_DIR/.env.production}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing backend env file: $ENV_FILE" >&2
  echo "Create it from backend/.env.production.example before running migrations." >&2
  exit 1
fi

if [[ ! -x "$VENV_DIR/bin/alembic" ]]; then
  echo "Missing Alembic executable: $VENV_DIR/bin/alembic" >&2
  echo "Create the virtualenv and install backend dependencies first." >&2
  exit 1
fi

set -a
# shellcheck source=/dev/null
source "$ENV_FILE"
set +a

cd "$BACKEND_DIR"
"$VENV_DIR/bin/alembic" upgrade head
