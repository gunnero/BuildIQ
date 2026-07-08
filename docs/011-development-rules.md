# Development Rules

## Product Boundary

BuildIQ V1 is standalone.

BuildIQ is not Kalveri OS.

V1 must not include AI features.

## AI Boundary

BuildIQ must never call OpenAI, Anthropic, Gemini, or any LLM provider directly. Future AI features must integrate only through Kalveri OS.

Do not add:

- Direct OpenAI integration
- Direct Anthropic integration
- Direct Gemini integration
- Provider SDKs for model generation
- Provider API keys
- Prompt templates
- AI chat features
- AI estimate generation

Future AI features must send work requests only to Kalveri OS.

## Language Rules

- User interface: Macedonian
- PDF outputs: Macedonian
- User-facing validation messages: Macedonian
- Codebase: English
- Database names: English
- API routes: English
- Documentation: English

## Backend Rules

- Use Python and FastAPI.
- Use PostgreSQL as the primary database.
- Use SQLAlchemy for ORM models.
- Use Alembic for migrations.
- Use JWT authentication.
- Enforce company ownership checks for customer, project, payment, expense, and estimate data.

## Frontend Rules

- Use React and TypeScript.
- Use Vite.
- Use TailwindCSS.
- Use React Router for routing.
- Use TanStack Query for server state.
- Use React Hook Form and Zod for forms and validation.
- Display all user-facing UI copy in Macedonian.

## Database Rules

- Use English table and column names.
- Store MKD currency amounts in clearly named fields ending with `_mkd`.
- Store payment status as one of `unpaid`, `partially_paid`, `paid`, or `overdue`.
- Store payment method as one of `cash`, `bank`, `card`, or `other`.
- Preserve payment history.

## Calculation Rules

- Calculations must be deterministic.
- Store calculation inputs and outputs.
- Do not use AI for V1 calculations.
- Keep formulas auditable.
- Use metric units.

## Documentation Rules

- Keep documentation in English.
- Update docs when architecture, boundaries, modules, APIs, database design, calculations, or payment rules change.

## Commit Rules

- Keep commits focused.
- Do not mix backend implementation, frontend implementation, and documentation-only changes unless the task explicitly requires it.
- Preserve the AI boundary in every feature.
