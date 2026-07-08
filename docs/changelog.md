# Changelog

## 2026-07-08

- Implemented Sprint 20 estimate PDF backend.
- Added company-scoped estimate document metadata, Macedonian PDF quote generation from stored estimate revision data, local storage under `BUILDIQ_STORAGE_PATH`, tenant-isolated PDF metadata/download endpoints, and tests proving PDF access and totals formatting stay backend-owned.
- Implemented Sprint 19 payments and expenses frontend.
- Added backend-backed payment list/create/detail/reverse/archive flows, expense category list/create/edit/archive flows, expense list/create/detail/reverse/archive flows, project financial summary display, typed financial API helpers, Macedonian financial UI states, confirmation prompts, and frontend tests proving financial values come from backend responses.
- Implemented Sprint 18 estimate frontend.
- Added backend-backed estimate list/create/detail/status/archive flows, create-from-calculation actions, revision and item display/edit/archive flows, typed estimate API helpers, Macedonian estimate UI states, and frontend tests proving estimate totals come from backend responses.
- Implemented Sprint 17 painting calculation frontend.
- Added backend-backed calculation run history, calculation engine status display, painting calculation submission, calculation detail output rendering, typed calculation/material API helpers, Macedonian calculation UI states, and frontend tests proving calculation values come from backend responses.
- Implemented Sprint 16 project, room, and measurement frontend.
- Added backend-backed project list/create/detail/edit/archive views, project status badges, timeline/status history display, task create/edit/status/archive flows, room create/edit/archive flows, opening create/edit/archive flows, measurement set/item flows, typed project/room/measurement API helpers, Macedonian UI states, and frontend tests for project/room/measurement workflows.
- Implemented Sprint 15 customer and property frontend.
- Added backend-backed customer list/create/detail/edit/archive/contact flows, property list/create/detail/edit/archive/contact/note flows, typed customer/property API helpers, Macedonian customer/property UI states, and frontend tests for customer/property workflows.
- Implemented Sprint 14 frontend authentication and dashboard wiring.
- Connected the login flow to backend auth, added current user/company/subscription session hydration, global 401 token clearing, protected route loading states, real dashboard identity data, Macedonian first-step guidance, and frontend auth/dashboard tests.
- Implemented Sprint 13 frontend foundation.
- Added React, TypeScript, Vite, TailwindCSS, React Router, TanStack Query, React Hook Form, Zod, API client, auth token storage, protected route shell, Macedonian navigation, login page, empty states, frontend tests, and frontend README.
- Implemented Sprint 12 backend stabilization and API contract.
- Added OpenAPI tag metadata, OpenAPI export command, exported `docs/api/openapi.json`, shared error helpers, audit helper, key audit events, and additive timestamp response fields for API consistency.
- Implemented Sprint 11 backend Payment and Expense Engine.
- Added company-scoped payment, payment allocation, expense category, and expense models with Alembic migration.
- Added tenant-isolated payment/expense APIs, reversal/archive endpoints, positive amount validation, project agreed-price fallback, and backend-owned project financial summaries.
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
