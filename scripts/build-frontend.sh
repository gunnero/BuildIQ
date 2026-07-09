#!/usr/bin/env bash
set -Eeuo pipefail

# Build the BuildIQ frontend for production.
# Run from any directory after reviewing docs/033-production-deployment-web01.md.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"
ENV_FILE="${FRONTEND_ENV_FILE:-$FRONTEND_DIR/.env.production}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing frontend env file: $ENV_FILE" >&2
  echo "Create it from frontend/.env.production.example before building." >&2
  exit 1
fi

cd "$FRONTEND_DIR"

if [[ ! -d node_modules ]]; then
  npm ci
fi

npm run build
