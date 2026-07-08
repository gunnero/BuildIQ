# BuildIQ Frontend

React, TypeScript, Vite, and TailwindCSS frontend for BuildIQ.

## Scope

Sprint 13 provides the frontend foundation only:

- React app scaffold in `frontend/`
- TailwindCSS styling
- React Router protected routes
- TanStack Query provider
- React Hook Form and Zod login form
- Backend API client using `VITE_API_BASE_URL`
- Authentication token storage
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

## Language Rules

- User-facing UI text is Macedonian.
- Code, route names, component names, and API fields are English.
- Future validation and notification text must remain Macedonian.
