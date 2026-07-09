# Production Deployment: web01

This document describes the deployment plan for controlled BuildIQ v0.9 RC1 validation on `web01` at `buildiq.kalveri.com`. It is not production approval; close the blockers in `docs/034-buildiq-v0.9-rc1-audit.md` before go-live.

BuildIQ V1 remains standalone and has no AI features. Do not add provider SDKs, API keys, prompts, or direct AI integrations during deployment.

## Target

- Server: `web01`
- Domain: `buildiq.kalveri.com`
- Frontend: React production build served by the web server
- Backend: FastAPI served on `127.0.0.1` behind reverse proxy
- Database: PostgreSQL
- PDF storage: local server storage path

Recommended server paths:

- Repository: `/home/buildiq/BuildIQ`
- Virtualenv: `/home/buildiq/BuildIQ/.venv`
- Frontend web root: `/var/www/buildiq`
- PDF storage: `/home/buildiq/storage`
- Backend env file: `/home/buildiq/BuildIQ/backend/.env.production`
- Frontend env file: `/home/buildiq/BuildIQ/frontend/.env.production`

## Server Prerequisites

Install system packages on `web01`:

```bash
sudo apt update
sudo apt install -y \
  git \
  python3 \
  python3-venv \
  python3-pip \
  fonts-dejavu-core \
  postgresql \
  postgresql-contrib \
  nodejs \
  npm \
  rsync \
  nginx \
  certbot \
  python3-certbot-nginx
```

Use the Node.js version required by the frontend lockfile. If the distribution package is too old, install an approved Node.js LTS runtime before building.

Create a service user if it does not already exist:

```bash
sudo useradd --system --create-home --shell /bin/bash buildiq
sudo install -d -o buildiq -g buildiq -m 750 /home/buildiq/storage
sudo install -d -o buildiq -g buildiq -m 755 /var/www/buildiq
```

## Git Clone And Pull Flow

Initial clone:

```bash
sudo -iu buildiq
git clone https://github.com/gunnero/BuildIQ.git /home/buildiq/BuildIQ
cd /home/buildiq/BuildIQ
git checkout develop
git pull --ff-only origin develop
```

Before each deployment, record the currently deployed commit:

```bash
cd /home/buildiq/BuildIQ
git rev-parse HEAD
```

Update code:

```bash
cd /home/buildiq/BuildIQ
git status --short
git fetch origin develop
git pull --ff-only origin develop
```

The working tree should be clean before deployment. Do not deploy uncommitted local edits.

## Python Backend Setup

Create and install the backend virtualenv:

```bash
sudo -iu buildiq
cd /home/buildiq/BuildIQ
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ./backend
```

The backend is started from `/home/buildiq/BuildIQ/backend`.

## Frontend Build Setup

Install frontend dependencies and build:

```bash
sudo -iu buildiq
cd /home/buildiq/BuildIQ/frontend
npm ci
npm run build
```

Copy the generated static files to the web root:

```bash
sudo rsync -a --delete /home/buildiq/BuildIQ/frontend/dist/ /var/www/buildiq/
sudo chown -R www-data:www-data /var/www/buildiq
```

The helper script `scripts/build-frontend.sh` always runs `npm ci` and then `npm run build` so the production build matches `package-lock.json` even when `node_modules` already exists.

## PostgreSQL Database Setup

Create the production database and user. Choose a strong password and store it only on `web01`.

```bash
sudo -u postgres createuser --pwprompt buildiq
sudo -u postgres createdb -O buildiq buildiq
```

Confirm connectivity from the server:

```bash
psql "postgresql://buildiq:REPLACE_WITH_PASSWORD@127.0.0.1:5432/buildiq" -c "select 1;"
```

The SQLAlchemy URL used by the backend must use the `psycopg` driver:

```text
postgresql+psycopg://buildiq:REPLACE_WITH_PASSWORD@127.0.0.1:5432/buildiq
```

## Environment Variables

Copy the examples and edit the real files on `web01` only:

```bash
cd /home/buildiq/BuildIQ
cp backend/.env.production.example backend/.env.production
cp frontend/.env.production.example frontend/.env.production
chmod 600 backend/.env.production frontend/.env.production
```

Backend production env:

Generate a high-entropy signing secret on `web01` and paste the output into the server-only env file:

```bash
python3 -c 'import secrets; print(secrets.token_urlsafe(48))'
```

```bash
BUILDIQ_ENV=production
BUILDIQ_DEBUG=false
BUILDIQ_SECRET_KEY=REPLACE_WITH_A_UNIQUE_64_CHARACTER_RANDOM_SECRET
BUILDIQ_DATABASE_URL=postgresql+psycopg://buildiq:REPLACE_WITH_PASSWORD@127.0.0.1:5432/buildiq
BUILDIQ_ALLOWED_ORIGINS=https://buildiq.kalveri.com
BUILDIQ_STORAGE_PATH=/home/buildiq/storage
```

Frontend production env:

```bash
VITE_API_BASE_URL=https://buildiq.kalveri.com
```

Never commit `backend/.env.production`, `frontend/.env.production`, database passwords, JWT secrets, or generated PDFs.

If a secret contains shell-special characters, quote it in the env file before using `source`, for example `BUILDIQ_SECRET_KEY='replace-with-real-secret'`.

If the database password contains URL-reserved characters, percent-encode it before placing it in `BUILDIQ_DATABASE_URL`; do not paste an unescaped password into the SQLAlchemy URL.

## Alembic Migration Command

Run migrations after pulling code and before restarting the backend:

```bash
sudo -iu buildiq
cd /home/buildiq/BuildIQ/backend
set -a
source .env.production
set +a
../.venv/bin/alembic upgrade head
```

Or use the helper:

```bash
cd /home/buildiq/BuildIQ
scripts/run-backend-migrations.sh
```

## Seed Command For Test/Demo Only

The seed command creates local/demo accounts and demo business data. Do not run it against production customer data.

For a temporary RC demo environment only:

```bash
sudo -iu buildiq
cd /home/buildiq/BuildIQ/backend
set -a
source .env.production
set +a
BUILDIQ_ENV=demo \
BUILDIQ_SEED_HQ_PASSWORD='UNIQUE_DEMO_PASSWORD_1' \
BUILDIQ_SEED_OWNER_PASSWORD='UNIQUE_DEMO_PASSWORD_2' \
BUILDIQ_SEED_ALEKSANDAR_PASSWORD='UNIQUE_DEMO_PASSWORD_3' \
BUILDIQ_SEED_HRISTIJAN_PASSWORD='UNIQUE_DEMO_PASSWORD_4' \
../.venv/bin/buildiq-seed-dev
```

Delete or disable demo accounts before real customer testing if the environment is no longer a demo sandbox.

## systemd Backend Service Example

Create `/etc/systemd/system/buildiq-backend.service`:

```ini
[Unit]
Description=BuildIQ FastAPI backend
After=network.target postgresql.service

[Service]
User=buildiq
Group=buildiq
WorkingDirectory=/home/buildiq/BuildIQ/backend
EnvironmentFile=/home/buildiq/BuildIQ/backend/.env.production
ExecStart=/home/buildiq/BuildIQ/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable buildiq-backend
sudo systemctl start buildiq-backend
sudo systemctl status buildiq-backend
```

Check the local backend:

```bash
curl http://127.0.0.1:8000/health
```

If Gunicorn is preferred later, add it as an explicit operational dependency after review. Do not silently change runtime dependencies during RC1 deployment.

## nginx Reverse Proxy Example

Create `/etc/nginx/sites-available/buildiq.kalveri.com`:

```nginx
server {
    listen 80;
    server_name buildiq.kalveri.com;

    root /var/www/buildiq;
    index index.html;

    client_max_body_size 20m;

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Enable it:

```bash
sudo ln -s /etc/nginx/sites-available/buildiq.kalveri.com /etc/nginx/sites-enabled/buildiq.kalveri.com
sudo nginx -t
sudo systemctl reload nginx
```

## Apache Reverse Proxy Example

If `web01` uses Apache instead of nginx, enable required modules:

```bash
sudo a2enmod proxy proxy_http rewrite headers ssl
```

Example virtual host:

```apache
<VirtualHost *:80>
    ServerName buildiq.kalveri.com
    DocumentRoot /var/www/buildiq

    ProxyPreserveHost On
    ProxyPass /api/ http://127.0.0.1:8000/api/
    ProxyPassReverse /api/ http://127.0.0.1:8000/api/
    ProxyPass /health http://127.0.0.1:8000/health
    ProxyPassReverse /health http://127.0.0.1:8000/health

    <Directory /var/www/buildiq>
        Require all granted
        RewriteEngine On
        RewriteBase /
        RewriteRule ^index\.html$ - [L]
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule . /index.html [L]
    </Directory>
</VirtualHost>
```

Validate and reload:

```bash
sudo apachectl configtest
sudo systemctl reload apache2
```

## SSL And Let's Encrypt Notes

Confirm DNS points `buildiq.kalveri.com` to `web01` before requesting a certificate.

For nginx:

```bash
sudo certbot --nginx -d buildiq.kalveri.com
```

For Apache:

```bash
sudo certbot --apache -d buildiq.kalveri.com
```

After SSL is active:

```bash
curl -I https://buildiq.kalveri.com
curl https://buildiq.kalveri.com/health
sudo certbot renew --dry-run
```

The frontend must call `https://buildiq.kalveri.com/api/v1`.

## Deployment Helper Script

After manual review, the deployment can be run from the repository root on `web01`:

```bash
sudo -iu buildiq
cd /home/buildiq/BuildIQ
scripts/deploy-web01.sh --confirm
```

The helper:

- refuses to run without `--confirm`
- refuses a dirty working tree unless `ALLOW_DIRTY=1` is explicitly set
- pulls `develop` with `--ff-only`
- installs backend dependencies into `.venv`
- runs Alembic migrations
- builds the frontend
- syncs `frontend/dist/` to `/var/www/buildiq`
- restarts `buildiq-backend`
- reloads nginx or Apache if a matching service exists

## Deployment Checklist

- DNS for `buildiq.kalveri.com` points to `web01`.
- PostgreSQL database and user exist.
- `/home/buildiq/storage` exists and is writable by the `buildiq` user.
- `backend/.env.production` exists with real secrets and production database URL.
- `frontend/.env.production` exists with `VITE_API_BASE_URL=https://buildiq.kalveri.com`.
- Repository is clean before deployment.
- Current deployed commit is recorded.
- Backend dependencies install successfully.
- Frontend dependencies install successfully.
- Alembic migrations complete.
- Frontend build completes.
- systemd backend service starts.
- Reverse proxy config validates.
- SSL certificate is issued and HTTPS loads.
- `https://buildiq.kalveri.com/health` returns healthy status.
- Login works with the intended test account.
- PDF generation writes files under `/home/buildiq/storage`.
- No secrets, generated PDFs, or local env files are committed.

## Rollback Checklist

Use rollback only after identifying the bad deployment commit and the previously healthy commit.

1. Record current failing commit:

   ```bash
   cd /home/buildiq/BuildIQ
   git rev-parse HEAD
   ```

2. Stop backend while rolling back code:

   ```bash
   sudo systemctl stop buildiq-backend
   ```

3. Check out the previously healthy commit:

   ```bash
   sudo -iu buildiq
   cd /home/buildiq/BuildIQ
   git fetch origin develop
   git checkout PREVIOUS_HEALTHY_COMMIT
   ```

4. Reinstall backend dependencies if the commit changed dependencies:

   ```bash
   .venv/bin/python -m pip install -e ./backend
   ```

5. Rebuild and resync frontend:

   ```bash
   scripts/build-frontend.sh
   sudo rsync -a --delete frontend/dist/ /var/www/buildiq/
   ```

6. Start backend and reload reverse proxy:

   ```bash
   sudo systemctl start buildiq-backend
   sudo systemctl reload nginx
   ```

7. Verify:

   ```bash
   curl https://buildiq.kalveri.com/health
   ```

Database migrations are not automatically reversible. If a rollback requires database changes, stop and create a separate database rollback plan from backups before changing production data.
