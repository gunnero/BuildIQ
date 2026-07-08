# Security

BuildIQ security starts with company isolation, backend-owned business logic, and auditability.

## Security Principles

- Every customer-owned record is company-scoped.
- Authorization is enforced in the backend.
- Frontend checks are convenience only.
- Sensitive actions create audit logs.
- Important business records are not hard-deleted.
- V1 has no AI provider credentials or provider SDKs.

## Authentication

V1 uses JWT authentication.

Authentication implementation should include:

- Secure password hashing
- Short-lived access tokens
- Refresh strategy when implemented
- Logout handling
- Inactive employee blocking
- Last login tracking

## Authorization

Authorization must support:

- Company isolation
- Employee roles
- Permissions
- Object-level checks
- HQ-specific access rules

Permission checks must protect:

- Customer data
- Project data
- Measurements
- Estimates
- Payments
- Expenses
- Supplier agreements
- Price books
- Subscriptions
- Feature flags
- Audit logs

## Company Isolation

Backend queries must include company scope for customer-owned data.

APIs must not allow an employee from one company to access another company's data by changing route IDs.

## Financial Security

Payment and expense changes must be audited.

Voiding financial records requires a reason and permission.

Financial history must remain recoverable.

## Estimate and PDF Security

Generated PDFs must be linked to company, project, estimate, and estimate revision.

PDF access must require authorization.

Public sharing, if added later, must use explicit share tokens with expiry and audit logs.

## BuildIQ HQ Security

HQ users must be separate from company employees.

HQ support access must be audited.

HQ subscription changes must preserve before and after state.

## Secrets

Secrets must not be committed.

Do not commit:

- Database passwords
- JWT secrets
- API keys
- Provider credentials
- Bank account admin credentials

## AI and Provider Boundary

BuildIQ must never call OpenAI, Anthropic, Gemini, or any LLM provider directly. Future AI features must integrate only through Kalveri OS.

No LLM provider credentials belong in BuildIQ.

## Audit Logs

Audit logs must record:

- Acting user
- Company
- Action
- Target entity
- Timestamp
- Before snapshot where useful
- After snapshot where useful

Audit logs must not be hard-deleted.
