# Development Standards

These standards guide BuildIQ implementation after the Blueprint v1.0 documentation phase.

## Scope

This document does not implement backend, frontend, migrations, AI, or provider SDKs.

## Stack

Backend:

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- JWT authentication

Frontend:

- React
- TypeScript
- Vite
- TailwindCSS
- React Router
- TanStack Query
- React Hook Form
- Zod

## Language Standards

- UI: Macedonian
- PDFs: Macedonian
- Validation messages: Macedonian
- Notifications: Macedonian
- Code: English
- Database: English
- API routes: English
- Comments: English
- Documentation: English

## Backend Standards

- Backend owns business logic.
- Backend calculates construction quantities.
- Backend resolves prices.
- Backend calculates financial totals.
- Backend generates PDFs from stored business data.
- Backend enforces company scope.
- Backend writes audit logs for sensitive actions.

## Frontend Standards

- Frontend collects inputs.
- Frontend displays backend-calculated values.
- Frontend must not calculate quantities or prices.
- Frontend must not decide payment status.
- Frontend must not resolve price source.
- Frontend must show Macedonian UI copy.

## Database Standards

- Customer-owned tables include `company_id`.
- Important business records preserve history.
- Estimates preserve revisions.
- Price books preserve validity windows.
- Supplier agreements preserve terms history.
- Payments and expenses are voided, not hard-deleted.
- Financial amounts use MKD-specific column names.

## API Standards

- API routes are English.
- API payload fields are English.
- User-facing errors are Macedonian.
- Mutations must validate company ownership.
- Sensitive mutations must audit.
- V1 API must not expose AI provider routes.

## AI Standards

BuildIQ must never call OpenAI, Anthropic, Gemini, or any LLM provider directly. Future AI features must integrate only through Kalveri OS.

Do not add:

- Provider SDKs
- Provider API keys
- Prompt templates
- Direct model calls
- AI chat UI
- AI estimate generation in V1

## Testing Standards

When implementation begins, tests should cover:

- Company isolation
- Authentication and authorization
- Calculation formulas
- Price resolution order
- Estimate revision history
- Payment totals
- Outstanding balance
- Expense voiding
- PDF generation inputs
- Macedonian validation messages

## Documentation Standards

Update Blueprint docs when implementation changes:

- Domain model
- Entity relationships
- Database design
- Business rules
- Calculation rules
- Procurement rules
- Financial rules
- Subscription rules
- API principles
- UI behavior
- Security model

## Commit Standards

- Keep commits focused.
- Do not mix unrelated implementation and documentation changes.
- Do not commit secrets.
- Do not add runtime behavior when the task is documentation-only.
