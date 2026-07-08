# API Principles

BuildIQ API routes and payload fields must be English.

User-facing validation messages returned by the API must be Macedonian.

## Base Path

V1 routes should use:

`/api/v1`

## Core API Rules

- Backend owns all business logic.
- Frontend submits facts and user intent.
- Frontend must not calculate construction quantities or prices.
- All customer-owned resources must be company-scoped.
- Object-level authorization is required.
- Important business records must preserve history.
- V1 has no AI routes.
- Future AI routes must hand work to Kalveri OS, not an LLM provider.

## Authentication

Authentication routes:

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

JWT authentication is planned for V1.

## Route Groups

Planned route groups:

- `/api/v1/companies`
- `/api/v1/employees`
- `/api/v1/roles`
- `/api/v1/permissions`
- `/api/v1/customers`
- `/api/v1/properties`
- `/api/v1/projects`
- `/api/v1/tasks`
- `/api/v1/rooms`
- `/api/v1/measurements`
- `/api/v1/calculations`
- `/api/v1/materials`
- `/api/v1/suppliers`
- `/api/v1/stores`
- `/api/v1/supplier-agreements`
- `/api/v1/price-books`
- `/api/v1/estimates`
- `/api/v1/payments`
- `/api/v1/expenses`
- `/api/v1/documents`
- `/api/v1/reports`
- `/api/v1/subscription`

BuildIQ HQ route groups may use:

- `/api/v1/hq/companies`
- `/api/v1/hq/subscriptions`
- `/api/v1/hq/manual-payments`
- `/api/v1/hq/feature-flags`
- `/api/v1/hq/audit-logs`

## Request Rules

- IDs in routes are English.
- Request field names are English.
- Dates use ISO 8601.
- Money values use MKD fields ending in `_mkd`.
- Mutating requests must be authorized.
- Sensitive mutations should create audit logs.

## Response Rules

Responses should include backend-calculated totals.

Examples:

- Project outstanding balance
- Payment status
- Material total
- Estimate total
- Expense total

Frontend must display these values, not recalculate them.

## Validation Errors

Validation error payload fields may be English, but message text must be Macedonian.

Example:

```json
{
  "field": "amount_mkd",
  "message": "Внесете валиден износ."
}
```

## Pagination and Filtering

List routes should support:

- Pagination
- Sorting
- Search
- Status filters
- Date filters where relevant

## History APIs

History-preserving resources should expose history intentionally.

Examples:

- Estimate revisions
- Price book validity
- Supplier agreement changes
- Payment and expense void history
- Audit logs

## AI Prohibition

No V1 API endpoint may call OpenAI, Anthropic, Gemini, or any LLM provider.
