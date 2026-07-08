# Changelog

## 2026-07-08

- Implemented Sprint 2 backend identity and tenant foundation.
- Added company, user, role, permission, subscription, feature flag, and audit log models with Alembic migration.
- Added password hashing, JWT login, current user, current company, role/permission helpers, and current subscription endpoints.
- Added local development seed command for HQ admin, demo company owner, base roles, starter plan, and subscription.
- Added backend tests for login, authentication guard, tenant-scoped company reads, current subscription reads, and password hashing.
- Renamed legacy brand references to Kalveri and KMI (Kalveri Market Intelligence).
- Updated the AI boundary to require future AI features to integrate only through Kalveri OS.
- Added BuildIQ Blueprint v1.0 documentation covering constitution, domain model, entity relationships, database blueprint, business rules, calculation, procurement, financial, subscription, HQ, API, UI, security, development standards, and product backlog.
- Updated README to reference Kalveri OS and BuildIQ Blueprint v1.0.

## 2026-07-03

- Initialized BuildIQ repository structure.
- Added project overview, architecture, AI boundary, V1 module, database, API, UI language, calculation, payment, expense, roadmap, and development rule documentation.
- Added README with purpose, domain, repository, stack, V1 scope, AI boundary, and development rules.
