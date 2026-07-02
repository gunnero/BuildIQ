# BuildIQ

BuildIQ is a Macedonian-first construction calculator and project/payment management platform.

## Purpose

BuildIQ helps construction teams calculate material needs, prepare offers, manage projects, track customer payments, record expenses, and generate Macedonian PDF quotes.

## Domain

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

BuildIQ must never call OpenAI, Anthropic, Gemini, or any other LLM provider directly. Future AI features must integrate through OneFiveFour OS. OneFiveFour OS owns AI Employees, Knowledge, Brains, Providers, Assignments, Brain Sessions, and Brain Responses.

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
- Construction calculations must be deterministic and auditable.
- Payment tracking must store agreed project price, total paid, remaining amount, payment history, payment date, payment method, payment note, and payment status.
- Backend and frontend implementation will be added after this documentation scaffold.
