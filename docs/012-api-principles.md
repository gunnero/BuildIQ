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

## OpenAPI Contract

FastAPI must generate a valid OpenAPI contract for the backend.

During backend development, export the contract with:

```bash
cd backend
../.venv/bin/buildiq-export-openapi
```

The generated file is stored at:

`docs/api/openapi.json`

Every endpoint should have a clear OpenAPI tag and summary. V1 backend tags are:

- `health`
- `auth`
- `companies`
- `subscriptions`
- `customers`
- `properties`
- `projects`
- `tasks`
- `rooms`
- `measurements`
- `materials`
- `procurement`
- `calculations`
- `estimates`
- `payments`
- `expenses`

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

Resource responses should use consistent field names:

- `id` for the resource identifier.
- `company_id` for company-scoped customer-owned records.
- `created_at` and `updated_at` for mutable records with timestamp columns.
- `created_at` for immutable history or audit rows that do not have an update timestamp.
- `archived_at` for records that support archive workflows.

List endpoints should use predictable ordering. The default order is `created_at` ascending unless a workflow-specific order is clearer, such as revision number, sort order, or latest active subscription.

List endpoints should exclude archived records unless the endpoint is explicitly a history or detail view where archived records are intentionally readable.

## Validation Errors

Validation error payload fields may be English, but message text must be Macedonian.

Example:

```json
{
  "field": "amount_mkd",
  "message": "Внесете валиден износ."
}
```

Backend code should use shared error helpers for common API failures:

- not found
- forbidden or cross-tenant access
- validation failure
- archived record access
- invalid state transition

The current API keeps existing `detail` message behavior for compatibility, with Macedonian user-facing message text.

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

Sensitive mutations should create audit logs without overcomplicating normal route code. Current low-risk audit events include login success, project creation, estimate status changes, payment creation, and payment reversal.

## AI Prohibition

No V1 API endpoint may call OpenAI, Anthropic, Gemini, or any LLM provider.
