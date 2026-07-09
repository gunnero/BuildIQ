# BuildIQ Frontend

React, TypeScript, Vite, and TailwindCSS frontend for BuildIQ.

## Scope

Sprint 21 wires estimate PDF quote actions to the backend document endpoints and keeps earlier customer, property, project, room, measurement, calculation, estimate, payment, and expense workflows available:

- React app scaffold in `frontend/`
- TailwindCSS styling
- React Router protected routes
- TanStack Query provider
- React Hook Form and Zod login form
- Backend API client using `VITE_API_BASE_URL`
- Authentication token storage
- Login integration with `POST /api/v1/auth/login`
- Session hydration with `GET /api/v1/auth/me`
- Company context from `GET /api/v1/companies/me`
- Subscription context from `GET /api/v1/subscription/me`
- Global 401 handling that clears the stored token
- Customer list, create, detail, edit, archive, and contact creation from `/api/v1/customers`
- Property list, create, detail, edit, archive, contact creation, and note creation from `/api/v1/properties`
- Project list, create, detail, edit, archive, status badge, timeline, and status history from `/api/v1/projects`
- Project task list, create, edit, status change, and archive actions from `/api/v1/projects/{project_id}/tasks` and `/api/v1/tasks`
- Project room list, create, detail, edit, archive, and backend-computed room area display from `/api/v1/projects/{project_id}/rooms`
- Room opening list, create, edit, and archive actions from `/api/v1/rooms/{room_id}/openings` and `/api/v1/openings`
- Measurement set list, create, and detail display from `/api/v1/projects/{project_id}/measurement-sets`
- Measurement item list, create, edit, and archive actions from `/api/v1/measurement-sets/{measurement_set_id}/items` and `/api/v1/measurement-items`
- Calculation engine list from `/api/v1/calculation-engines`
- Calculation run history and detail display from `/api/v1/calculations`
- Painting calculation submission through `POST /api/v1/calculations/run`
- Backend-returned painting output, assumptions, warnings, and line item display
- Estimate list, manual creation, detail, status changes, and archive actions from `/api/v1/estimates`
- Estimate creation from completed calculations through `/api/v1/estimates/from-calculation/{calculation_run_id}`
- Estimate revision display from `/api/v1/estimates/{estimate_id}/revisions` and `/api/v1/estimate-revisions/{revision_id}`
- Estimate item list, create, edit, and archive actions from `/api/v1/estimate-revisions/{revision_id}/items` and `/api/v1/estimate-items`
- Backend-returned estimate totals and estimate item totals
- Estimate PDF generation from `/api/v1/estimates/{estimate_id}/pdf`
- Generated estimate document display from the backend response
- Estimate PDF download from `/api/v1/estimate-documents/{document_id}/download`
- Payment list, create, detail, reverse, and archive actions from `/api/v1/payments`
- Expense category list, create, edit, and archive actions from `/api/v1/expense-categories`
- Expense list, create, detail, reverse, and archive actions from `/api/v1/expenses`
- Project financial summary display from `/api/v1/projects/{project_id}/financial-summary`
- Backend-returned financial summary, payment, and expense values
- Macedonian layout, navigation, login page, and empty states

The frontend does not calculate construction quantities, room areas, selected areas, liters, material costs, labor costs, estimate totals, PDF totals, payment totals, expense totals, prices, payment statuses, outstanding balances, profit, or business totals. Those values must come from backend API responses.

## Local Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Default backend URL:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Scripts

```bash
npm run dev
npm run build
npm run lint
npm test
```

## Routes

- `/login`
- `/dashboard`
- `/customers`
- `/projects`
- `/materials`
- `/suppliers`
- `/calculations`
- `/estimates`
- `/payments`
- `/expenses`
- `/settings`

## Customers and Properties

The `/customers` route displays a backend-backed workspace for:

- customer list, creation, detail, editing, archive actions, and customer contacts
- property list, creation linked to a customer, detail, editing, archive actions, property contacts, and property notes

The page does not calculate quantities, prices, project totals, payment statuses, or derived business values.

## Projects, Rooms, and Measurements

The `/projects` route displays a backend-backed workspace ordered as:

- overview
- finances
- tasks
- rooms
- measurements
- later placeholders for calculations, estimates, payments, photos, and documents

The page supports project create/edit/archive, project status display, timeline and status history display, task create/edit/status/archive, room create/edit/archive, opening create/edit/archive, measurement set create/detail, and measurement item create/edit/archive.

Room detail displays `floor_area`, `ceiling_area`, `wall_area_gross`, `wall_area_net`, and `total_paintable_area` returned by the backend. The frontend only formats those values for display.

The finance section displays `accepted_estimate_total`, `agreed_project_price`, `revenue_basis`, `total_received_payments`, `total_pending_payments`, `outstanding_balance`, `total_recorded_expenses`, `estimated_profit`, and `payment_status` returned by the backend.

## Calculations

The `/calculations` route displays a backend-backed workspace for:

- registered calculation engines, with implemented engines shown as available and placeholders shown as in preparation
- calculation run history with engine type, status, linked project/room, and created date
- painting calculation submission using selected project, optional task, optional room, optional measurement set, paint options, material selections, waste percentage, labor rate, and notes
- calculation detail with input payload, output payload, assumptions, warnings, and line items returned by the backend

The painting form sends inputs to the backend with `engine_type=painting`. The frontend does not derive totals, liters, selected area, material cost, labor cost, or line item values locally.

## Estimates

The `/estimates` route displays a backend-backed workspace for:

- estimate list with customer, project, status, created date, and latest revision total
- manual estimate creation linked to a project
- estimate creation from completed calculation runs
- estimate metadata, revisions, selected revision detail, items, and backend totals
- item create, edit, and archive actions when the backend allows the revision to be edited
- status actions for sent, accepted, rejected, and archive
- PDF quote generation and download through backend document endpoints

The calculation detail page also exposes `Креирај понуда` for completed calculation runs. The action calls the backend estimate-from-calculation endpoint and does not copy, price, or total line items in the browser.

Estimate totals shown in the UI come from `subtotal`, `discount_total`, `adjustment_total`, `tax_total`, and `total` on backend revision responses. Item totals come from backend `total_price` values.

The estimate detail page exposes `Генерирај PDF понуда`. The action sends the selected revision ID to the backend, displays the returned document metadata, and downloads PDFs from the backend document download endpoint. The frontend does not render PDF files or calculate PDF totals.

## Payments

The `/payments` route displays a backend-backed workspace for:

- payment list with customer, project, method, status, and amount
- payment creation linked to customer, project, and optionally estimate
- payment detail with backend amount, status, method, date, note, reversal, archive, and allocation data
- reverse and archive actions with user confirmation

Payment methods are displayed in Macedonian as `Кеш`, `Банкарски трансфер`, `Картичка`, and `Друго`.

## Expenses

The `/expenses` route displays a backend-backed workspace for:

- expense category list, creation, editing, and archive actions
- expense list with category, project, method, status, and amount
- expense creation linked optionally to project, category, and material
- expense detail with backend amount, status, method, date, note, reversal, and archive data
- reverse and archive actions with user confirmation

The frontend only formats payment and expense amounts returned by the backend. It does not derive project balance, status, or profit.

## Authentication

The login page submits credentials to the backend and stores the returned access token in local storage. Protected routes load the current user, company, and subscription from the backend before rendering the app shell.

Logout clears the stored token and redirects the user to `/login`.

## Language Rules

- User-facing UI text is Macedonian.
- Code, route names, component names, and API fields are English.
- Future validation and notification text must remain Macedonian.
