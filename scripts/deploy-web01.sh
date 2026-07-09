#!/usr/bin/env bash
set -Eeuo pipefail

# BuildIQ web01 deployment helper.
# Review docs/033-production-deployment-web01.md before running.
# Usage on web01 from the repository root:
#   scripts/deploy-web01.sh --confirm

if [[ "${1:-}" != "--confirm" ]]; then
  echo "Refusing to deploy without explicit confirmation." >&2
  echo "Usage: scripts/deploy-web01.sh --confirm" >&2
  exit 2
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-$ROOT_DIR/.venv}"
WEB_ROOT="${WEB_ROOT:-/var/www/buildiq}"
BACKEND_SERVICE="${BACKEND_SERVICE:-buildiq-backend}"
BRANCH="${BRANCH:-develop}"

cd "$ROOT_DIR"

if [[ -n "$(git status --short)" && "${ALLOW_DIRTY:-0}" != "1" ]]; then
  echo "Working tree is dirty. Commit, stash, or set ALLOW_DIRTY=1 after manual review." >&2
  git status --short >&2
  exit 1
fi

git fetch origin "$BRANCH"
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"

if [[ ! -d "$VENV_DIR" ]]; then
  python3 -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -e "$ROOT_DIR/backend"

"$ROOT_DIR/scripts/run-backend-migrations.sh"
"$ROOT_DIR/scripts/build-frontend.sh"

sudo install -d -o www-data -g www-data -m 755 "$WEB_ROOT"
sudo rsync -a --delete "$ROOT_DIR/frontend/dist/" "$WEB_ROOT/"
sudo chown -R www-data:www-data "$WEB_ROOT"

sudo systemctl restart "$BACKEND_SERVICE"

if systemctl list-unit-files nginx.service >/dev/null 2>&1; then
  sudo systemctl reload nginx
elif systemctl list-unit-files apache2.service >/dev/null 2>&1; then
  sudo systemctl reload apache2
else
  echo "No nginx.service or apache2.service found; reload the reverse proxy manually." >&2
fi

echo "BuildIQ deployment helper completed for $BRANCH."
