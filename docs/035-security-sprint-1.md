# BuildIQ Security Sprint 1

Date: 2026-07-09
Branch: `develop`
Scope: permissions, production configuration, demo seed credentials, and subscription access

## Status

Implemented and covered by backend tests. This sprint keeps the existing tenant/company model and adds enforcement at the shared authenticated-company boundary.

## RC1 Permission Matrix

| Role | Permissions |
| --- | --- |
| owner | Full company business access |
| manager | Customer, property, project, task, room, measurement, material, procurement, calculation, estimate, payment, and expense read/write access |
| worker | Read projects, tasks, rooms, measurements; create measurement sets/items and calculation runs; no financial, procurement, project/task archive, or pricing mutations |
| accountant | Read/write estimates, payments, and expenses; no measurement, project, room, or procurement mutations |

The backend maps each business request to a domain read/write permission. Frontend visibility remains convenience-only. An active user without a role is denied sensitive business access.

## Production Configuration Gate

When `BUILDIQ_ENV=production`, startup rejects empty, default, or short JWT secrets; debug mode; wildcard, HTTP, local, or development CORS origins; relative storage paths; and SQLite database URLs. The gate is implemented in `backend/app/core/config.py` and covered by `backend/tests/test_config.py`.

## Seed Credential Gate

`buildiq-seed-dev` now requires four unique passwords of at least 12 characters for the HQ admin, demo owner, Aleksandar test owner, and Hristijan test owner. It refuses production unless `BUILDIQ_ALLOW_DEMO_SEED_IN_PRODUCTION=true` is explicitly set. That override is intended only for an isolated, temporary demo environment; it does not relax the password requirements.

No default demo password is documented or accepted by the seed command.

## Subscription Gate

Business APIs require the latest company subscription to be `active` or `trialing`, within its configured start/end/trial dates. Suspended, cancelled, expired, missing, and otherwise inactive subscriptions receive `403`. Authentication, health, current-company, and current-subscription inspection remain available so an operator can diagnose access state.

## Validation

- Backend tests, including the Security Sprint 1 negative tests, pass.
- Frontend tests, lint, and production build remain required release gates.
- Provider and secret scans must remain clean; seed passwords are supplied through environment variables and never committed.
