# UI Specification

BuildIQ UI is Macedonian-first.

## Language Rules

- UI text must be Macedonian.
- Validation messages must be Macedonian.
- Notifications must be Macedonian.
- PDF labels and text must be Macedonian.
- Code, route names, and API fields remain English.

## UI Architecture Rules

- Frontend collects user input.
- Frontend displays backend results.
- Frontend must never calculate construction quantities or prices.
- Frontend must not decide payment status.
- Frontend must not resolve material prices.
- Frontend must not generate business totals independently.

## Main Navigation

Expected Macedonian navigation areas:

- Dashboard
- Customers
- Projects
- Tasks
- Suppliers
- Price Books
- Estimates
- Payments
- Expenses
- Reports
- Settings

Final UI labels must be Macedonian.

## Core Screens

### Authentication

- Login
- Password reset when implemented
- Current user profile

### Dashboard

Dashboard should show backend-provided summaries:

- Active projects
- Outstanding balance
- Recent payments
- Recent expenses
- Overdue projects
- Estimate status summary

### Customers and Properties

Customer screens should support:

- Customer list
- Customer profile
- Customer properties
- Customer projects
- Customer payment history

### Projects

Project screens should support:

- Project overview
- Tasks
- Rooms
- Measurements
- Calculations
- Material list
- Estimates
- Payments
- Expenses
- Documents

### Rooms and Measurements

Measurement forms collect:

- Length
- Width
- Height
- Area
- Perimeter
- Opening area
- Quantity

The backend returns derived calculation results.

### Calculators

Calculator screens support:

- Painting
- Tile
- Knauf
- Flooring

The UI sends inputs to the backend and displays returned results.

### Procurement

Procurement screens support:

- Suppliers
- Stores
- Supplier agreements
- Price books
- Retail prices
- Negotiated company prices
- Project price overrides

### Estimates

Estimate screens support:

- Estimate list
- Estimate draft
- Estimate revisions
- Accepted revision
- PDF generation

Estimate revisions must make history visible.

### Payments and Expenses

Financial screens display:

- Agreed project price
- Total paid
- Outstanding balance
- Payment history
- Expense history

Values come from the backend.

### Subscription

Company subscription screens may show:

- Current plan
- Subscription status
- Manual bank transfer instructions
- Payment review status

### BuildIQ HQ

HQ UI is separate from company UI.

HQ screens support:

- Companies
- Subscriptions
- Manual payment review
- Feature flags
- Audit logs

## PDF Output

PDF offers/quotes must be Macedonian and generated from backend-owned estimate revision data.

PDFs should include:

- Company details
- Customer details
- Project details
- Estimate number
- Revision number
- Issue date
- Valid-until date
- Line items
- Totals
- Payment terms
- Notes

## Empty States and Notifications

Empty states and notifications must be Macedonian and action-oriented.

Examples of intent:

- No customers yet
- No rooms added
- Estimate revision created
- Payment recorded
- Subscription payment pending review

## Accessibility

UI implementation should use semantic HTML, keyboard-accessible controls, readable contrast, and clear form error placement.
