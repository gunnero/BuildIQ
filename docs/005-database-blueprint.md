# Database Blueprint

This document defines the conceptual database blueprint for BuildIQ v1.0. It is not an Alembic migration.

## Naming Rules

- Tables use English plural names.
- Columns use English snake_case names.
- API-facing IDs use UUIDs unless implementation later chooses another documented strategy.
- MKD money fields end with `_mkd`.
- Customer-owned records include `company_id`.
- Important business records use archival, status, voiding, or supersession instead of hard delete.

## Shared Columns

Most company-owned tables should include:

- `id`
- `company_id`
- `created_at`
- `updated_at`
- `archived_at`

Important audited tables should also include:

- `created_by_employee_id`
- `updated_by_employee_id`
- `archived_by_employee_id`

## Kernel Tables

### companies

- `id`
- `name`
- `tax_number`
- `address`
- `phone`
- `email`
- `status`
- `created_at`
- `updated_at`

### feature_flags

- `id`
- `key`
- `name`
- `description`
- `default_enabled`
- `created_at`
- `updated_at`

### feature_flag_assignments

- `id`
- `company_id`
- `employee_id`
- `feature_flag_id`
- `enabled`
- `created_at`
- `updated_at`

### audit_logs

- `id`
- `company_id`
- `acting_employee_id`
- `entity_type`
- `entity_id`
- `action`
- `before_snapshot`
- `after_snapshot`
- `ip_address`
- `user_agent`
- `created_at`

## Identity Tables

### employees

- `id`
- `company_id`
- `name`
- `email`
- `password_hash`
- `status`
- `last_login_at`
- `created_at`
- `updated_at`

### roles

- `id`
- `company_id`
- `name`
- `description`
- `is_system_role`
- `created_at`
- `updated_at`

### permissions

- `id`
- `key`
- `name`
- `description`

### role_permissions

- `id`
- `role_id`
- `permission_id`

### employee_roles

- `id`
- `employee_id`
- `role_id`

## Customer and Project Tables

### customers

- `id`
- `company_id`
- `name`
- `phone`
- `email`
- `address`
- `note`
- `status`
- `created_at`
- `updated_at`
- `archived_at`

### properties

- `id`
- `company_id`
- `customer_id`
- `name`
- `address`
- `city`
- `note`
- `created_at`
- `updated_at`
- `archived_at`

### projects

- `id`
- `company_id`
- `customer_id`
- `property_id`
- `name`
- `description`
- `address`
- `project_status`
- `payment_status`
- `agreed_price_mkd`
- `total_paid_mkd`
- `outstanding_balance_mkd`
- `start_date`
- `due_date`
- `accepted_estimate_revision_id`
- `created_at`
- `updated_at`
- `archived_at`

### tasks

- `id`
- `company_id`
- `project_id`
- `title`
- `description`
- `status`
- `assigned_employee_id`
- `due_date`
- `completed_at`
- `created_at`
- `updated_at`
- `archived_at`

### rooms

- `id`
- `company_id`
- `project_id`
- `name`
- `floor`
- `note`
- `created_at`
- `updated_at`
- `archived_at`

### measurements

- `id`
- `company_id`
- `project_id`
- `room_id`
- `measurement_type`
- `length_m`
- `width_m`
- `height_m`
- `area_m2`
- `perimeter_m`
- `opening_area_m2`
- `quantity`
- `input_snapshot`
- `created_at`
- `updated_at`
- `archived_at`

## Calculation and Material Tables

### calculation_runs

- `id`
- `company_id`
- `project_id`
- `room_id`
- `calculator_type`
- `calculator_version`
- `input_snapshot`
- `result_snapshot`
- `created_by_employee_id`
- `created_at`

### materials

- `id`
- `company_id`
- `name`
- `category`
- `unit`
- `description`
- `default_waste_percent`
- `created_at`
- `updated_at`
- `archived_at`

### material_list_items

- `id`
- `company_id`
- `project_id`
- `room_id`
- `material_id`
- `calculation_run_id`
- `description`
- `unit`
- `quantity`
- `unit_price_mkd`
- `total_price_mkd`
- `price_source`
- `created_at`
- `updated_at`
- `archived_at`

## Procurement Tables

### suppliers

- `id`
- `company_id`
- `name`
- `tax_number`
- `phone`
- `email`
- `address`
- `note`
- `status`
- `created_at`
- `updated_at`
- `archived_at`

### stores

- `id`
- `company_id`
- `supplier_id`
- `name`
- `address`
- `phone`
- `email`
- `created_at`
- `updated_at`
- `archived_at`

### supplier_agreements

- `id`
- `company_id`
- `supplier_id`
- `agreement_number`
- `status`
- `starts_on`
- `ends_on`
- `terms_snapshot`
- `created_at`
- `updated_at`
- `archived_at`

### price_books

- `id`
- `company_id`
- `supplier_id`
- `name`
- `status`
- `currency`
- `valid_from`
- `valid_until`
- `created_at`
- `updated_at`
- `archived_at`

### price_book_items

- `id`
- `company_id`
- `price_book_id`
- `material_id`
- `supplier_sku`
- `retail_price_mkd`
- `negotiated_company_price_mkd`
- `unit`
- `valid_from`
- `valid_until`
- `created_at`
- `updated_at`

### project_price_overrides

- `id`
- `company_id`
- `project_id`
- `material_id`
- `unit_price_mkd`
- `reason`
- `created_by_employee_id`
- `created_at`
- `superseded_at`

## Estimate and Financial Tables

### estimates

- `id`
- `company_id`
- `project_id`
- `customer_id`
- `estimate_number`
- `status`
- `current_revision_id`
- `created_at`
- `updated_at`
- `archived_at`

### estimate_revisions

- `id`
- `company_id`
- `estimate_id`
- `revision_number`
- `status`
- `issue_date`
- `valid_until`
- `subtotal_mkd`
- `discount_mkd`
- `tax_mkd`
- `total_mkd`
- `notes`
- `terms`
- `source_snapshot`
- `created_by_employee_id`
- `created_at`
- `accepted_at`
- `voided_at`

### estimate_items

- `id`
- `company_id`
- `estimate_revision_id`
- `description`
- `unit`
- `quantity`
- `unit_price_mkd`
- `total_price_mkd`
- `source_type`
- `source_id`
- `sort_order`

### payments

- `id`
- `company_id`
- `project_id`
- `customer_id`
- `amount_mkd`
- `payment_date`
- `payment_method`
- `note`
- `status`
- `created_by_employee_id`
- `created_at`
- `voided_at`

### expenses

- `id`
- `company_id`
- `project_id`
- `category`
- `description`
- `amount_mkd`
- `expense_date`
- `payment_method`
- `supplier_id`
- `note`
- `created_by_employee_id`
- `created_at`
- `voided_at`

## Document and Reporting Tables

### documents

- `id`
- `company_id`
- `project_id`
- `estimate_id`
- `estimate_revision_id`
- `document_type`
- `language`
- `storage_path`
- `source_snapshot`
- `created_by_employee_id`
- `created_at`
- `voided_at`

### report_snapshots

- `id`
- `company_id`
- `report_type`
- `filters_snapshot`
- `result_snapshot`
- `created_by_employee_id`
- `created_at`

## Subscription Tables

### subscriptions

- `id`
- `company_id`
- `plan_key`
- `status`
- `starts_on`
- `ends_on`
- `trial_ends_on`
- `created_at`
- `updated_at`

### subscription_payments

- `id`
- `company_id`
- `subscription_id`
- `amount_mkd`
- `payment_date`
- `payment_method`
- `bank_reference`
- `status`
- `reviewed_by_hq_employee_id`
- `reviewed_at`
- `note`
- `created_at`

## Integration Tables

### integration_requests

- `id`
- `company_id`
- `integration_type`
- `status`
- `request_snapshot`
- `response_snapshot`
- `created_at`
- `completed_at`

V1 must not use integration requests for AI provider calls.
