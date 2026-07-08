# Entity Relationships

This document describes conceptual relationships for BuildIQ Blueprint v1.0. It is not a migration file.

## Tenant Boundary

`companies` is the tenant root.

All customer-owned data must include `company_id`.

Internal BuildIQ HQ records may be platform-scoped, but they must not bypass authorization rules.

## Relationship Map

```mermaid
erDiagram
    companies ||--o{ employees : owns
    companies ||--o{ roles : defines
    roles ||--o{ role_permissions : grants
    permissions ||--o{ role_permissions : included_in
    employees ||--o{ employee_roles : assigned
    roles ||--o{ employee_roles : assigned_to

    companies ||--o{ customers : owns
    customers ||--o{ properties : has
    customers ||--o{ projects : requests
    properties ||--o{ projects : hosts

    projects ||--o{ tasks : contains
    projects ||--o{ rooms : contains
    rooms ||--o{ measurements : has
    rooms ||--o{ calculation_runs : calculated_for
    calculation_runs ||--o{ material_list_items : produces

    companies ||--o{ materials : catalogs
    companies ||--o{ suppliers : works_with
    suppliers ||--o{ stores : operates
    suppliers ||--o{ supplier_agreements : signs
    companies ||--o{ price_books : owns
    price_books ||--o{ price_book_items : contains
    projects ||--o{ project_price_overrides : overrides

    projects ||--o{ estimates : has
    estimates ||--o{ estimate_revisions : preserves
    estimate_revisions ||--o{ estimate_items : contains

    projects ||--o{ payments : receives
    projects ||--o{ expenses : incurs
    projects ||--o{ documents : generates

    companies ||--o{ audit_logs : records
    companies ||--o{ feature_flag_assignments : receives
    companies ||--o{ subscriptions : has
    subscriptions ||--o{ subscription_payments : paid_by
```

## Core Relationship Rules

- A company can have many employees.
- An employee belongs to one company.
- A role belongs to one company unless it is a system role template.
- A role can contain many permissions.
- An employee can have many roles.
- A customer belongs to one company.
- A customer can have many properties.
- A project belongs to one company and one customer.
- A project can optionally belong to one property.
- A project can have many tasks, rooms, estimates, payments, expenses, and documents.
- A room belongs to one project.
- A measurement belongs to one room and one project.
- A calculation run belongs to one project and may belong to one room.
- Material list items belong to one project and may be linked to a calculation run.
- Suppliers and stores belong to a company.
- Supplier agreements belong to a company and supplier.
- Price books belong to a company and may be linked to suppliers.
- Project price overrides belong to a project and preserve project-specific pricing decisions.
- Estimates belong to projects.
- Estimate revisions belong to estimates and must preserve historical offer versions.
- Payments and expenses belong to projects and must preserve history.

## History Relationships

The following relationships must preserve historical snapshots:

- Estimate to estimate revision
- Estimate revision to estimate items
- Supplier agreement to agreement terms
- Price book to price book items
- Project price override to project material price
- Payment to project financial state
- Expense to project financial state
- Generated document to source estimate revision

## Feature Flags

Feature flags may be global, company-scoped, or employee-scoped.

Resolution order:

1. Employee assignment
2. Company assignment
3. Global default

## Audit Logs

Audit logs should link to:

- Company
- Acting employee
- Entity type
- Entity ID
- Action
- Before snapshot where useful
- After snapshot where useful
- Timestamp

Audit logs must not be hard-deleted.
