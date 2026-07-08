# Roadmap

BuildIQ V1 is a standalone construction calculator and project/payment management platform with no AI features.

## Phase 1: Documentation Scaffold

- Create repository structure.
- Define product purpose.
- Define architecture.
- Define AI boundary.
- Define V1 modules.
- Define database design.
- Define API design.
- Define UI language rules.
- Define calculation rules.
- Define payment and expense rules.

## Phase 2: Backend Foundation

- Add FastAPI application.
- Add PostgreSQL connection.
- Add SQLAlchemy models.
- Add Alembic migrations.
- Add JWT authentication.
- Add company/user access boundaries.

## Phase 3: Frontend Foundation

- Add React, TypeScript, and Vite.
- Add TailwindCSS.
- Add routing.
- Add API client.
- Add form and validation patterns.
- Add Macedonian UI shell.

## Phase 4: Core Workflows

- Customers
- Projects
- Rooms
- Measurements
- Calculators
- Material list
- Estimates/offers
- Payments
- Expenses
- Dashboard

## Phase 5: PDF Offers

- Generate Macedonian PDF offers/quotes.
- Include company, customer, project, room, material, labor, total, payment, and note details.

## Post-V1: Kalveri OS Integration

Future AI features must integrate only through Kalveri OS.

BuildIQ must never call OpenAI, Anthropic, Gemini, or any LLM provider directly.
