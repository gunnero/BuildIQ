# Architecture

BuildIQ V1 is a standalone web application for construction calculations and project/payment management.

## Planned Stack

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

Infrastructure:

- Docker Compose for local services
- Local `storage/` directory for generated files during development

## High-Level Components

- `backend/`: future FastAPI application, domain services, database models, API routes, authentication, and PDF generation.
- `frontend/`: future React application, Macedonian UI, forms, dashboards, and estimate/payment screens.
- `database/migrations/`: future Alembic migrations.
- `database/seeds/`: future seed data for local development.
- `database/schema/`: future schema references or exported database design artifacts.
- `docker/`: future Docker support files.
- `docs/`: product, architecture, API, database, and development documentation.
- `storage/`: generated files and local runtime artifacts that should not be committed except for `.gitkeep`.

## Runtime Boundaries

BuildIQ owns:

- Construction workflows
- Calculations
- Customers
- Projects
- Rooms
- Measurements
- Material lists
- Estimates and offers
- Payments
- Expenses
- Reports
- PDFs

Kalveri OS owns future AI capabilities:

- AI Employees
- Knowledge
- Brains
- Providers
- Assignments
- Brain Sessions
- Brain Responses

## Data Flow

1. The frontend sends authenticated requests to the FastAPI backend.
2. The backend validates input and applies construction/domain rules.
3. The backend persists records in PostgreSQL through SQLAlchemy models and Alembic-managed schema.
4. The backend generates Macedonian PDF offers/quotes from project, calculation, estimate, and payment data.
5. The frontend displays Macedonian user-facing screens, statuses, validation errors, and dashboard summaries.

## Authentication

V1 uses JWT authentication. Users belong to companies. Access control must prevent users from reading or modifying records owned by another company.

## AI Boundary

BuildIQ must never call OpenAI, Anthropic, Gemini, or any LLM provider directly. Future AI features must integrate only through Kalveri OS.
