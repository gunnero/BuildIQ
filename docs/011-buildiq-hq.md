# BuildIQ HQ

BuildIQ HQ is the internal admin panel for operating the BuildIQ platform.

## Purpose

BuildIQ HQ helps internal staff manage platform operations without entering customer workflows as normal company users.

## HQ Responsibilities

BuildIQ HQ can manage:

- Companies
- Company subscription status
- Manual subscription payments by bank transfer
- Feature flags
- Support visibility
- Audit logs
- Platform announcements
- Plan configuration
- Account suspension and reactivation

## HQ Must Not Own Customer Workflows

BuildIQ HQ must not become the place where construction projects are managed.

Customer-owned workflows remain in company-scoped BuildIQ:

- Customers
- Properties
- Projects
- Tasks
- Rooms
- Measurements
- Calculations
- Estimates
- Payments
- Expenses
- PDFs

## Access Control

HQ access must be separate from company employee access.

HQ roles may include:

- Platform owner
- Support admin
- Billing admin
- Read-only auditor

HQ actions must be audited.

## Company Support Visibility

Support views may allow HQ staff to inspect company data for support purposes.

Rules:

- Access must be permission-protected.
- Access must be audited.
- Sensitive actions should require elevated permission.
- Financial changes should be avoided unless explicitly part of support workflow.

## Feature Flags

HQ can manage feature flags.

Feature flag scopes:

- Global
- Company
- Employee

Feature flags are operational controls, not permission replacements.

## Subscription Operations

HQ can:

- Review bank transfer payments.
- Approve manual subscription payments.
- Reject manual subscription payments.
- Extend trial dates.
- Suspend companies.
- Reactivate companies.

All subscription changes must preserve history.

## Audit Logs

HQ audit logs must show:

- Acting HQ user
- Action
- Target company
- Target entity
- Before snapshot where useful
- After snapshot where useful
- Timestamp
- IP address where available

Audit logs must not be hard-deleted.
