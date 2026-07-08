# Domain Model

BuildIQ Blueprint v1.0 defines the business domain before implementation.

## Domain Principles

- BuildIQ is company-first.
- Every customer-owned object belongs to a company.
- Backend services own all domain decisions.
- Frontend screens collect inputs and display backend responses.
- Business history is preserved instead of overwritten.
- V1 has no AI.
- Future AI integrates only through Kalveri OS.

## Core Engines

| Engine | Responsibility |
| --- | --- |
| BuildIQ Kernel | Shared company scope, feature flags, audit logging, currency, units, and cross-engine rules. |
| Identity Engine | Employees, roles, permissions, authentication, and access control. |
| Customer Engine | Customers, properties, customer contacts, and customer history. |
| Project Engine | Projects, tasks, rooms, statuses, ownership, and project lifecycle. |
| Measurement Engine | Room dimensions, openings, surfaces, measurement snapshots, and metric units. |
| Calculation Engine | Deterministic construction calculations and calculation result snapshots. |
| Material Engine | Materials, material list items, units, quantities, and material history. |
| Procurement Engine | Suppliers, stores, supplier agreements, price books, retail prices, negotiated company prices, and project price overrides. |
| Estimate Engine | Estimates, estimate revisions, estimate items, approval workflow, and accepted project price. |
| Financial Engine | Payments, expenses, total paid, outstanding balance, and financial reporting inputs. |
| Document Engine | Macedonian PDFs, quote generation, document metadata, and document history. |
| Reporting Engine | Dashboard metrics, project summaries, payment summaries, expense summaries, and operational reports. |
| Subscription Engine | BuildIQ subscription state, manual bank transfer payments, plan access, and future online payment provider abstraction. |
| Integration Engine | Future integrations, including Kalveri OS handoff for AI features after V1. |

## Companies

A company is the tenant boundary for BuildIQ customer-owned data.

Companies own:

- Employees
- Roles and permissions assignments
- Customers
- Properties
- Projects
- Rooms
- Measurements
- Materials
- Suppliers and stores
- Supplier agreements
- Price books
- Estimates and revisions
- Payments
- Expenses
- Documents
- Reports
- Subscription status

## Employees

Employees are users inside a company.

Employees can be assigned roles and permissions. The backend must enforce permissions for all sensitive actions.

Examples:

- Owner
- Admin
- Estimator
- Project manager
- Accountant
- Employee

## Roles and Permissions

Roles group permissions. Permissions authorize concrete actions.

Example permission areas:

- Customer management
- Project management
- Measurement entry
- Estimate approval
- Payment recording
- Expense recording
- Supplier and price book management
- Report access
- Company settings

## Customers and Properties

Customers are the people or organizations receiving construction work.

Properties are physical locations owned by or associated with customers. A customer may have multiple properties, and projects may be tied to a property.

## Projects, Tasks, and Rooms

Projects represent construction work for a customer and optional property.

Tasks represent actionable work inside a project.

Rooms group measurements, calculations, materials, and estimate scope by physical space.

## Measurements

Measurements store construction input facts such as length, width, height, area, perimeter, openings, and quantities.

Measurements are not final business prices. They feed backend calculations.

## Materials

Materials represent construction goods and consumables.

Materials can come from:

- Calculation outputs
- Manual project entries
- Supplier catalogs
- Price books
- Project-specific overrides

## Suppliers, Stores, Agreements, and Price Books

Suppliers and stores represent places where materials are purchased.

Supplier agreements define negotiated pricing terms for a company.

Price books preserve retail prices and negotiated company prices over time.

Project price overrides allow a project-specific price to supersede standard pricing while preserving history.

## Estimates and Estimate Revisions

An estimate is a customer-facing offer.

Estimate revisions preserve each version of the offer. Accepted revisions define the commercial basis for the project agreed price.

## Payments, Expenses, and Outstanding Balance

Payments record money received from customers.

Expenses record project costs.

Outstanding balance is calculated by the backend:

`outstanding_balance_mkd = agreed_price_mkd - total_paid_mkd`

## Subscriptions

BuildIQ subscriptions control access to the platform.

V1 supports manual subscription payments by bank transfer. Future online payment providers must be introduced through an abstraction, not hard-coded provider logic.

## BuildIQ HQ

BuildIQ HQ is the internal admin panel for operating the BuildIQ platform.

It manages companies, subscription state, manual payment reviews, feature flags, support visibility, and audit logs.
