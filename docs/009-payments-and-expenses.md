# Payments and Expenses

BuildIQ V1 must support project payment tracking and project expense tracking.

## Payment Requirements

The system must store:

- Agreed project price
- Total paid
- Remaining amount
- Payment history
- Payment date
- Payment method
- Payment note
- Payment status

## Payment Methods

Database values:

- `cash`
- `bank`
- `card`
- `other`

## Payment Statuses

Database values:

- `unpaid`
- `partially_paid`
- `paid`
- `overdue`

## Payment Calculations

`total_paid_mkd` is the sum of all payments for a project.

`remaining_amount_mkd = agreed_price_mkd - total_paid_mkd`

Status rules:

- `unpaid`: no payments received and the project is not overdue.
- `partially_paid`: total paid is greater than zero and less than agreed price.
- `paid`: total paid is greater than or equal to agreed price.
- `overdue`: remaining amount is greater than zero after the agreed due date.

## Payment Example

Customer: Aleksandar

Project agreed price: 40,000 MKD

Payment received: 20,000 MKD

Remaining balance: 20,000 MKD

Payment status: `partially_paid`

## Payment History

Each payment record must store:

- Project
- Customer
- Amount in MKD
- Payment date
- Payment method
- Payment note
- User who recorded the payment
- Creation timestamp

## Expenses

Expenses are project-related costs.

Common expense categories:

- Materials
- Labor
- Subcontractor
- Transport
- Tools
- Other

Each expense record should store:

- Project
- Amount in MKD
- Expense date
- Category
- Payment method
- Supplier name
- Description
- Note
- User who recorded the expense

## Dashboard Impact

The dashboard should show:

- Total agreed project value
- Total paid
- Remaining amount
- Overdue amount
- Total expenses
- Project profit estimate where enough data exists
