# BuildIQ Frontend

React, TypeScript, Vite, and TailwindCSS frontend for BuildIQ.

## Scope

Sprint 17 wires the painting calculation frontend to the backend calculation endpoints and keeps earlier customer, property, project, room, and measurement workflows available:

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
- Macedonian layout, navigation, login page, and empty states

The frontend does not calculate construction quantities, room areas, selected areas, liters, material costs, labor costs, prices, payment statuses, outstanding balances, or business totals. Those values must come from backend API responses.

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
- tasks
- rooms
- measurements
- later placeholders for calculations, estimates, payments, photos, and documents

The page supports project create/edit/archive, project status display, timeline and status history display, task create/edit/status/archive, room create/edit/archive, opening create/edit/archive, measurement set create/detail, and measurement item create/edit/archive.

Room detail displays `floor_area`, `ceiling_area`, `wall_area_gross`, `wall_area_net`, and `total_paintable_area` returned by the backend. The frontend only formats those values for display.

## Calculations

The `/calculations` route displays a backend-backed workspace for:

- registered calculation engines, with implemented engines shown as available and placeholders shown as in preparation
- calculation run history with engine type, status, linked project/room, and created date
- painting calculation submission using selected project, optional task, optional room, optional measurement set, paint options, material selections, waste percentage, labor rate, and notes
- calculation detail with input payload, output payload, assumptions, warnings, and line items returned by the backend

The painting form sends inputs to the backend with `engine_type=painting`. The frontend does not derive totals, liters, selected area, material cost, labor cost, or line item values locally.

## Authentication

The login page submits credentials to the backend and stores the returned access token in local storage. Protected routes load the current user, company, and subscription from the backend before rendering the app shell.

Logout clears the stored token and redirects the user to `/login`.

## Language Rules

- User-facing UI text is Macedonian.
- Code, route names, component names, and API fields are English.
- Future validation and notification text must remain Macedonian.
