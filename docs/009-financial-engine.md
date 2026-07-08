# Financial Engine

The Financial Engine manages project financial state, payments, expenses, outstanding balances, and reporting inputs.

## Core Rules

- Backend owns all financial calculations.
- Frontend must not calculate totals, outstanding balances, payment status, or profit.
- Financial records must preserve history.
- Payments and expenses must not be hard-deleted.
- UI, validation messages, notifications, and PDFs must show financial information in Macedonian.

## Project Financial Fields

Projects must track:

- `agreed_price_mkd`
- `total_paid_mkd`
- `outstanding_balance_mkd`
- `payment_status`

Formula:

`outstanding_balance_mkd = agreed_price_mkd - total_paid_mkd`

## Payment Methods

Allowed values:

- `cash`
- `bank`
- `card`
- `other`

## Payment Statuses

Allowed values:

- `unpaid`
- `partially_paid`
- `paid`
- `overdue`

## Payment History

Each payment records:

- Company
- Project
- Customer
- Amount in MKD
- Payment date
- Payment method
- Note
- Status
- Employee who recorded it
- Creation timestamp
- Voiding timestamp when applicable

## Payment Example

Customer: Aleksandar

Agreed project price: 40,000 MKD

Payment received: 20,000 MKD

Outstanding balance: 20,000 MKD

Payment status: `partially_paid`

## Expense History

Expenses record project costs.

Each expense records:

- Company
- Project
- Category
- Description
- Amount in MKD
- Expense date
- Payment method
- Supplier when applicable
- Note
- Employee who recorded it
- Creation timestamp
- Voiding timestamp when applicable

## Financial Dashboard Inputs

The Reporting Engine can use Financial Engine outputs for:

- Total agreed project value
- Total paid
- Outstanding balance
- Overdue amount
- Total expenses
- Estimated project margin
- Receivables by customer
- Receivables by project

## Accepted Estimate Link

When a customer accepts an estimate revision, the backend may set the project agreed price from that accepted revision.

The project must preserve a reference to the accepted estimate revision.

## Estimate Engine Implementation Status

Sprint 10 implements the backend Estimate Engine foundation:

- Company-scoped estimates, estimate revisions, and estimate items.
- Manual estimate creation for active company projects.
- Backend-calculated revision totals from active estimate items.
- Estimate status transitions for `draft`, `sent`, `accepted`, `rejected`, and `archived`.
- Immutable sent and accepted revisions.
- Estimate creation from completed calculation runs by copying calculation line items into historical estimate items.
- Archive endpoints instead of hard deletes.

Sprint 10 does not implement payments, expenses, invoices, online payments, PDF generation, or project agreed-price updates. Those remain later Financial and Document Engine work.

## Voiding Rules

Payments and expenses may be voided with a reason.

Voiding must create an audit log entry and recalculate project financial summaries.
