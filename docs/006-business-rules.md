# Business Rules

This document defines BuildIQ Blueprint v1.0 business rules.

## Core Rules

- BuildIQ is standalone in V1.
- V1 has no AI.
- Future AI features go only through Kalveri OS.
- Backend owns all business logic.
- Frontend must never calculate construction quantities or prices.
- UI, PDFs, validation messages, and notifications must be Macedonian.
- Code, database, API routes, comments, and docs must be English.

## Company Scope

All customer-owned data must be company-scoped with `company_id`.

Backend queries must enforce company scope for:

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
- Estimates
- Payments
- Expenses
- Documents
- Reports

## Deletion and Archival

Important business data must not be hard-deleted.

Allowed lifecycle actions:

- Archive
- Cancel
- Void
- Supersede
- Mark inactive

Hard delete may be allowed only for non-business drafts with no historical or financial impact, and only when documented.

## Estimate Rules

- Estimates must preserve revisions.
- Estimate revisions must snapshot line items and totals.
- Accepted estimate revisions may set or update project agreed price.
- A project should clearly reference the accepted estimate revision when one exists.
- Voided estimates remain in history.

## Pricing Rules

Backend price resolution must use this order:

1. Project price override
2. Negotiated company price
3. Retail price from active price book
4. Manual backend-approved price entry

The selected price source must be stored on material list items and estimate items.

## Procurement Rules

- Suppliers and stores belong to companies.
- Supplier agreements must preserve terms history.
- Price books must preserve valid dates.
- Retail prices and negotiated company prices must be stored separately.
- Project price overrides must preserve reason and author.

## Calculation Rules

- Calculations run only in the backend.
- Calculations must store input snapshots and result snapshots.
- Calculator versions must be recorded.
- Calculations must use metric units.
- Calculations must not use AI in V1.
- Frontend displays calculation results returned by the API.

## Payment Rules

Projects must store:

- Agreed project price
- Total paid
- Outstanding balance
- Payment status

Payments must store:

- Amount
- Date
- Method
- Note
- Status
- Author

Payment methods:

- `cash`
- `bank`
- `card`
- `other`

Payment statuses:

- `unpaid`
- `partially_paid`
- `paid`
- `overdue`

## Expense Rules

Expenses must preserve project cost history.

Expenses may be voided, but financial history must remain auditable.

## Subscription Rules

V1 supports manual subscription payments by bank transfer.

BuildIQ HQ reviews manual subscription payments and updates subscription status.

Future online payment providers must be introduced behind a provider abstraction.

No online payment provider SDK is allowed in the Blueprint documentation scaffold.

## Audit Rules

The backend must create audit logs for important actions:

- Login and authentication-sensitive changes
- Role and permission changes
- Customer archival
- Project archival
- Estimate approval, revision, voiding, and acceptance
- Payment creation or voiding
- Expense creation or voiding
- Supplier agreement changes
- Price book changes
- Project price overrides
- Subscription status changes
- Feature flag changes

Audit logs must not be hard-deleted.
