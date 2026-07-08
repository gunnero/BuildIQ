# BuildIQ Constitution v1.0

BuildIQ is a Macedonian-first construction calculator and project/payment management platform.

This constitution defines the non-negotiable product, architecture, language, data, and implementation boundaries for BuildIQ Blueprint v1.0.

## Product Identity

BuildIQ is a standalone product in V1.

BuildIQ is not Kalveri OS.

BuildIQ V1 has no AI.

BuildIQ serves construction businesses that need deterministic calculators, project management, customer records, payment tracking, expenses, reports, and Macedonian PDF offers.

## AI Boundary

BuildIQ must never call OpenAI, Anthropic, Gemini, or any LLM provider directly. Future AI features must integrate only through Kalveri OS.

Kalveri OS owns future AI capabilities:

- AI Employees
- Knowledge
- Brains
- Providers
- Assignments
- Brain Sessions
- Brain Responses

BuildIQ owns:

- Construction workflows
- Calculations
- Customers
- Properties
- Projects
- Tasks
- Rooms
- Measurements
- Materials
- Suppliers and stores
- Supplier agreements
- Price books
- Estimates and estimate revisions
- Payments
- Expenses
- Reports
- PDFs
- Subscription and access state for BuildIQ itself

## Language Contract

- UI text must be Macedonian.
- PDF output must be Macedonian.
- User-facing validation messages must be Macedonian.
- Notifications must be Macedonian.
- Code must be English.
- Database tables and columns must be English.
- API routes and payload field names must be English.
- Comments must be English.
- Documentation must be English.

## Architecture Rules

- Backend owns all business logic.
- Frontend must never calculate construction quantities or prices.
- Frontend may collect inputs and display backend results.
- Construction calculations must be deterministic, versioned, and auditable.
- Pricing decisions must be resolved by the backend.
- Financial calculations must be resolved by the backend.
- PDFs must be generated from backend-owned data.
- V1 must not include provider SDKs, provider API keys, prompt templates, AI chat, or AI-generated estimates.

## Data Ownership Rules

All customer-owned data must be scoped with `company_id`.

Company-scoped data includes:

- Employees
- Customers
- Properties
- Projects
- Tasks
- Rooms
- Measurements
- Materials
- Suppliers
- Supplier agreements
- Price books
- Project price overrides
- Estimates
- Estimate revisions
- Payments
- Expenses
- Documents
- Reports
- Audit logs

Internal BuildIQ HQ data may be platform-scoped, but access to it must be restricted to authorized internal administrators.

## Historical Integrity Rules

Important business data must not be hard-deleted.

The following records must preserve history:

- Estimates
- Estimate revisions
- Price books
- Supplier agreements
- Project price overrides
- Payments
- Expenses
- Financial records
- Subscription payments
- Audit logs
- Generated PDFs

Records may be archived, voided, cancelled, superseded, or soft-deleted when the workflow requires it.

## Core Engines

BuildIQ Blueprint v1.0 is organized around these engines:

- BuildIQ Kernel
- Identity Engine
- Customer Engine
- Project Engine
- Measurement Engine
- Calculation Engine
- Material Engine
- Procurement Engine
- Estimate Engine
- Financial Engine
- Document Engine
- Reporting Engine
- Subscription Engine
- Integration Engine

Each engine must expose backend-owned behavior through English API routes and Macedonian user-facing output.

## Implementation Boundary

This blueprint prepares the repository for implementation. It does not implement backend code, frontend code, database migrations, AI features, or provider SDKs.
