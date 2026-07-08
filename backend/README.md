# BuildIQ Backend

FastAPI backend kernel scaffold for BuildIQ Sprint 1.

## Scope

This scaffold includes:

- FastAPI application factory
- `/health` endpoint
- `/api/v1` router structure
- Environment-based configuration
- Basic logging setup
- PostgreSQL SQLAlchemy engine/session setup
- Alembic base configuration
- Pytest setup

This scaffold intentionally does not include:

- Frontend implementation
- Authentication implementation
- Customer, project, calculation, payment, supplier, estimate, or other business modules
- Domain model migrations
- AI features
- OpenAI, Anthropic, Gemini, or other LLM provider SDKs

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

## Run the App

```bash
cd backend
../.venv/bin/uvicorn app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

## Run Tests

```bash
cd backend
../.venv/bin/python -m pytest
```

## Alembic

Alembic is configured, but Sprint 1 does not create domain migrations or database tables.

When migrations are introduced later:

```bash
cd backend
../.venv/bin/alembic revision --autogenerate -m "message"
../.venv/bin/alembic upgrade head
```
