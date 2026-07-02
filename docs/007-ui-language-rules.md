# UI Language Rules

BuildIQ is Macedonian-first.

## Required Language Split

- User interface: Macedonian
- PDF outputs: Macedonian
- User-facing validation messages: Macedonian
- Codebase: English
- Database names: English
- API routes: English
- Documentation: English

## UI Copy

All labels, buttons, headings, empty states, navigation items, confirmation messages, and errors shown to users must be Macedonian.

Examples:

- Login: `Најава`
- Customers: `Клиенти`
- Projects: `Проекти`
- Rooms: `Простории`
- Measurements: `Мерења`
- Estimates / Offers: `Понуди`
- Payments: `Плаќања`
- Expenses: `Трошоци`
- Dashboard: `Контролна табла`
- Generate PDF: `Генерирај PDF`
- Total paid: `Вкупно платено`
- Remaining balance: `Преостанат износ`

## Payment Labels

Payment methods should be displayed in Macedonian:

- `cash`: `Готовина`
- `bank`: `Банка`
- `card`: `Картичка`
- `other`: `Друго`

Payment statuses should be displayed in Macedonian:

- `unpaid`: `Неплатено`
- `partially_paid`: `Делумно платено`
- `paid`: `Платено`
- `overdue`: `Доцни`

## Currency

Amounts should be shown in Macedonian denars:

- Code: `MKD`
- Display: `ден.`

Example:

`20,000 ден.`

## Validation Messages

Validation messages must be Macedonian even when API field names are English.

Examples:

- `Името на клиентот е задолжително.`
- `Внесете валиден износ.`
- `Датумот на плаќање е задолжителен.`
- `Проектот не е пронајден.`

## Developer Naming

Use English names in code, database fields, API routes, tests, and documentation.

Examples:

- `customers`
- `projects`
- `payment_status`
- `remaining_amount_mkd`
- `/api/v1/projects/{project_id}/payments`
