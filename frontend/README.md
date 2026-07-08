# BuildIQ Frontend

React, TypeScript, Vite, and TailwindCSS frontend for BuildIQ.

## Scope

Sprint 15 wires the customer and property frontend to the backend customer/property endpoints:

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
- Macedonian layout, navigation, login page, and empty states

The frontend does not calculate construction quantities, prices, payment statuses, outstanding balances, or business totals. Those values must come from backend API responses.

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

## Authentication

The login page submits credentials to the backend and stores the returned access token in local storage. Protected routes load the current user, company, and subscription from the backend before rendering the app shell.

Logout clears the stored token and redirects the user to `/login`.

## Language Rules

- User-facing UI text is Macedonian.
- Code, route names, component names, and API fields are English.
- Future validation and notification text must remain Macedonian.
