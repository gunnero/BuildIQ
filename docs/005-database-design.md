# Database Design

Database names must be English.

This document defines the conceptual V1 database model. Final SQLAlchemy models and Alembic migrations will be created during backend implementation.

## Core Tables

### companies

Stores each construction company using BuildIQ.

Suggested fields:

- `id`
- `name`
- `tax_number`
- `address`
- `phone`
- `email`
- `created_at`
- `updated_at`

### users

Stores login accounts and employees.

Suggested fields:

- `id`
- `company_id`
- `name`
- `email`
- `password_hash`
- `role`
- `is_active`
- `created_at`
- `updated_at`

### customers

Stores customer records.

Suggested fields:

- `id`
- `company_id`
- `name`
- `phone`
- `email`
- `address`
- `note`
- `created_at`
- `updated_at`

### projects

Stores construction projects.

Suggested fields:

- `id`
- `company_id`
- `customer_id`
- `name`
- `description`
- `address`
- `agreed_price_mkd`
- `total_paid_mkd`
- `remaining_amount_mkd`
- `payment_status`
- `project_status`
- `start_date`
- `due_date`
- `created_at`
- `updated_at`

Payment status values:

- `unpaid`
- `partially_paid`
- `paid`
- `overdue`

### rooms

Stores project rooms.

Suggested fields:

- `id`
- `company_id`
- `project_id`
- `name`
- `level`
- `note`
- `created_at`
- `updated_at`

### measurements

Stores room measurements.

Suggested fields:

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
- `note`
- `created_at`
- `updated_at`

### calculation_runs

Stores calculation results by project and room.

Suggested fields:

- `id`
- `company_id`
- `project_id`
- `room_id`
- `calculator_type`
- `input_snapshot`
- `result_snapshot`
- `created_by_user_id`
- `created_at`

Calculator type values:

- `painting`
- `tile`
- `knauf`
- `flooring`

### material_items

Stores generated or manually entered material list rows.

Suggested fields:

- `id`
- `company_id`
- `project_id`
- `room_id`
- `calculation_run_id`
- `name`
- `unit`
- `quantity`
- `unit_price_mkd`
- `total_price_mkd`
- `source`
- `note`
- `created_at`
- `updated_at`

### estimates

Stores offers/quotes.

Suggested fields:

- `id`
- `company_id`
- `project_id`
- `customer_id`
- `estimate_number`
- `status`
- `issue_date`
- `valid_until`
- `subtotal_mkd`
- `discount_mkd`
- `tax_mkd`
- `total_mkd`
- `notes`
- `terms`
- `created_at`
- `updated_at`

### estimate_items

Stores estimate line items.

Suggested fields:

- `id`
- `company_id`
- `estimate_id`
- `description`
- `unit`
- `quantity`
- `unit_price_mkd`
- `total_price_mkd`
- `sort_order`

### payments

Stores payment history.

Suggested fields:

- `id`
- `company_id`
- `project_id`
- `customer_id`
- `amount_mkd`
- `payment_date`
- `payment_method`
- `note`
- `created_by_user_id`
- `created_at`
- `updated_at`

Payment method values:

- `cash`
- `bank`
- `card`
- `other`

### expenses

Stores project expenses.

Suggested fields:

- `id`
- `company_id`
- `project_id`
- `category`
- `description`
- `amount_mkd`
- `expense_date`
- `payment_method`
- `supplier_name`
- `note`
- `created_by_user_id`
- `created_at`
- `updated_at`

## Payment Totals

Projects must store:

- `agreed_price_mkd`
- `total_paid_mkd`
- `remaining_amount_mkd`
- `payment_status`

`total_paid_mkd` is the sum of project payments.

`remaining_amount_mkd = agreed_price_mkd - total_paid_mkd`

Example:

- Customer: Aleksandar
- Agreed project price: 40,000 MKD
- Payment received: 20,000 MKD
- Remaining balance: 20,000 MKD
- Payment status: `partially_paid`
