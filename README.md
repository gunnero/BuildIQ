# BuildIQ

BuildIQ is a Macedonian-first construction calculator and project/payment management platform.

## Purpose

BuildIQ helps construction teams calculate material needs, prepare offers, manage projects, track customer payments, record expenses, and generate Macedonian PDF quotes.

## Domain

Production target: `buildiq.kalveri.com`

Temporary domain: `buildiq.razbudise.mk`

## Repository

GitHub: <https://github.com/gunnero/BuildIQ.git>

## Stack

Backend stack planned for V1:

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- JWT authentication

Frontend stack planned for V1:

- React
- TypeScript
- Vite
- TailwindCSS
- React Router
- TanStack Query
- React Hook Form
- Zod

## V1 Scope

V1 is a standalone product. It includes no AI features.

BuildIQ Blueprint v1.0 is the implementation contract for the first backend and frontend build. Start with [docs/000-buildiq-constitution.md](docs/000-buildiq-constitution.md), then follow the domain, database, business rule, engine, API, UI, security, and backlog documents in `docs/`.

V1 modules:

1. Authentication
2. Companies
3. Users / Employees
4. Customers
5. Projects
6. Rooms
7. Measurements
8. Painting calculator
9. Tile calculator
10. Knauf calculator
11. Flooring calculator
12. Material list
13. Estimates / Offers
14. Payments
15. Expenses
16. Dashboard
17. PDF quote generation

Core V1 workflow:

1. Log in
2. Create a customer
3. Create a project for that customer
4. Add one or more rooms
5. Enter room dimensions
6. Run construction calculations
7. Generate an estimate
8. Record payments
9. See how much the customer has paid
10. See how much the customer still owes
11. Generate a Macedonian PDF offer/quote

## AI Boundary

BuildIQ V1 has no AI.

BuildIQ must never call OpenAI, Anthropic, Gemini, or any LLM provider directly. Future AI features must integrate only through Kalveri OS. Kalveri OS owns AI Employees, Knowledge, Brains, Providers, Assignments, Brain Sessions, and Brain Responses.

BuildIQ owns construction workflows, calculations, customers, projects, payments, expenses, reports, and PDFs.

## Development Rules

- User interface text must be Macedonian.
- PDF output must be Macedonian.
- User-facing validation messages must be Macedonian.
- Codebase language must be English.
- Database names must be English.
- API routes must be English.
- Documentation must be English.
- V1 must remain standalone.
- V1 must not include AI features.
- BuildIQ must not include direct LLM provider SDKs, API keys, prompts, or provider-specific integrations.
- Backend owns all business logic.
- Frontend must never calculate construction quantities or prices.
- All customer-owned data must be company-scoped with `company_id`.
- Important business data must not be hard-deleted.
- Estimates, price books, supplier agreements, and financial records must preserve history.
- Construction calculations must be deterministic and auditable.
- Payment tracking must store agreed project price, total paid, remaining amount, payment history, payment date, payment method, payment note, and payment status.
- Backend implementation has started under `backend/`.
- Frontend foundation has started under `frontend/`.

## BuildIQ Blueprint v1.0

Blueprint documents:

- [BuildIQ Constitution](docs/000-buildiq-constitution.md)
- [Domain Model](docs/003-domain-model.md)
- [Entity Relationships](docs/004-entity-relationships.md)
- [Database Blueprint](docs/005-database-blueprint.md)
- [Business Rules](docs/006-business-rules.md)
- [Calculation Engine Framework](docs/007-calculation-engine-framework.md)
- [Procurement Engine](docs/008-procurement-engine.md)
- [Financial Engine](docs/009-financial-engine.md)
- [Subscription Engine](docs/010-subscription-engine.md)
- [BuildIQ HQ](docs/011-buildiq-hq.md)
- [API Principles](docs/012-api-principles.md)
- [UI Specification](docs/013-ui-specification.md)
- [Security](docs/014-security.md)
- [Development Standards](docs/015-development-standards.md)
- [Product Backlog](docs/018-product-backlog.md)

## Deployment

BuildIQ v0.9 RC1 is prepared for deployment to `web01` at `buildiq.kalveri.com`.

Production deployment documentation:

- [web01 production deployment guide](docs/033-production-deployment-web01.md)
