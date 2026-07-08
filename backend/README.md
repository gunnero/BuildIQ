# BuildIQ Backend

FastAPI backend for BuildIQ.

## Scope

The backend currently includes:

- FastAPI application factory
- `/health` endpoint
- `/api/v1` router structure
- Environment-based configuration
- Basic logging setup
- PostgreSQL SQLAlchemy engine/session setup
- Alembic base configuration
- Pytest setup
- Identity and tenant foundation
- Password hashing
- JWT access tokens
- Current user and current company dependencies
- Role and permission helper structure
- Company subscription read model
- Local development seed command

The backend intentionally does not include:

- Frontend implementation
- Customer, project, calculation, payment, supplier, estimate, or other business modules
- PDF generation
- AI features
- OpenAI, Anthropic, Gemini, LangChain, LlamaIndex, or other LLM/provider SDKs

Future AI features must integrate only through Kalveri OS.

## Local Setup

From the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e './backend[dev]'
cp .env.example .env
docker compose up -d postgres
```

Create and migrate the database:

```bash
cd backend
../.venv/bin/alembic upgrade head
```

Seed initial local development data:

```bash
cd backend
../.venv/bin/buildiq-seed-dev
```

Default local seed accounts:

- HQ admin: `hq@buildiq.local`
- Demo owner: `owner@demo.buildiq.local`

Both use `ChangeMe123!` unless overridden with:

```bash
BUILDIQ_SEED_HQ_PASSWORD='new-password' BUILDIQ_SEED_OWNER_PASSWORD='new-password' ../.venv/bin/buildiq-seed-dev
```

## Run the App

```bash
cd backend
../.venv/bin/uvicorn app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Authentication endpoints:

- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/companies/me`
- `GET /api/v1/subscription/me`

## Run Tests

```bash
cd backend
../.venv/bin/python -m pytest
```

## Alembic

Alembic is configured for PostgreSQL.

Current migration status:

- Identity and tenant foundation tables exist.
- No customer, project, calculation, payment, supplier, estimate, or PDF tables exist yet.

Migration commands:

```bash
cd backend
../.venv/bin/alembic heads
../.venv/bin/alembic upgrade head
```
