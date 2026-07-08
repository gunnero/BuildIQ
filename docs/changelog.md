# Changelog

## 2026-07-08

- Implemented Sprint 10 backend Estimate Engine.
- Added company-scoped estimate, estimate revision, and estimate item models with Alembic migration.
- Added tenant-isolated estimate APIs, backend-owned revision totals, status and archive endpoints, immutable sent/accepted revisions, and estimate creation from completed calculation runs.
- Implemented Sprint 9 backend Painting Engine.
- Added deterministic room/measurement-set area sourcing, paint/primer quantity formulas, material coverage validation, procurement price resolution, labor cost calculation, and painting line items.
- Updated calculation engine registry so painting is implemented while tiles, knauf, flooring, concrete, and facade remain placeholders.
- Implemented Sprint 8 backend Procurement Engine.
- Added company-scoped supplier, supplier contact, supplier agreement, price book, price book item, and project material price override models with Alembic migration.
- Added tenant-isolated procurement APIs, archive endpoints, backend-owned price resolution priority, validity date handling, cross-company link validation, and tests.
- Implemented Sprint 7 backend Material Engine.
- Added company-scoped material category, manufacturer, material, custom unit, and consumption rule models with Alembic migration.
- Added global default material units, tenant-isolated material catalog APIs, archive endpoints, consumption rule validation, and tests.
- Implemented Sprint 6 backend Calculation Engine Framework.
- Added company-scoped calculation run, input, output, and line item models with Alembic migration.
- Added tenant-isolated calculation framework APIs, placeholder engine registry, auditable stored input/output snapshots, archive endpoint, and tests.
- Implemented Sprint 5 backend Room and Measurement Engine.
- Added company-scoped room, room opening, measurement set, and measurement item models with Alembic migration.
- Added tenant-isolated room/opening/measurement APIs, backend-owned room area calculations, archive endpoints, and tests.
- Implemented Sprint 4 backend Project and Task Engine.
- Added company-scoped project, project task, project status history, and project timeline event models with Alembic migration.
- Added tenant-isolated project/task APIs with archive endpoints, project status history, project timeline events, and tests.
- Implemented Sprint 3 backend Customer and Property Engine.
- Added company-scoped customer, customer contact, property, property contact, and property note models with Alembic migration.
- Added tenant-isolated customer/property APIs with soft archive support and tests.
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
