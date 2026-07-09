# BuildIQ v0.9 RC1 Checklist

This checklist describes the BuildIQ v0.9 release candidate for first real-user testing.

## What Works

- Local authentication with the seeded demo owner account.
- Company and subscription context in the application shell.
- Customer and property list, create, detail, edit, archive, contacts, and property notes.
- Project list, create, detail, edit, archive, status history, timeline, and financial summary.
- Project tasks with create, edit, status change, and archive flows.
- Project rooms with backend-returned area values, openings, and archive flows.
- Measurement sets and measurement items.
- Painting calculation run history, engine status display, run form, result detail, assumptions, warnings, and line items.
- Estimate list, manual creation, creation from completed calculation, revisions, items, status actions, and backend totals.
- PDF quote generation and download from backend estimate data.
- Payment list, create, detail, reverse, and archive flows.
- Expense category and expense list, create, detail, reverse, and archive flows.
- Local MVP seed data that supports a demo from login to PDF download.

## Not Included Yet

- Production deployment hardening.
- Full frontend material catalog CRUD.
- Full frontend supplier/procurement CRUD.
- Tile, knauf, flooring, concrete, and facade calculation UIs and formulas.
- Invoices.
- Online payment provider integration.
- Photos and document management beyond estimate PDF documents.
- Advanced reporting dashboards.
- AI features. Future AI work must integrate only through Kalveri OS.

## Known Limitations

- v0.9 RC1 is intended for local and controlled first-user testing, not production use.
- The frontend is optimized for the MVP demo flow and does not yet cover every backend endpoint.
- PDF styling is intentionally simple and generated from stored estimate revision data.
- The current payment and expense flows preserve financial history, so test users should use reverse/archive actions instead of expecting edits.
- The application shows backend-returned totals and calculated values only; frontend display formatting must not be treated as calculation logic.
- Local demo credentials are for development only and must not be reused in production.

## Manual Test Checklist

- Start PostgreSQL or an equivalent local development database.
- Run backend migrations.
- Run `buildiq-seed-dev`.
- Start the backend API.
- Start the frontend with `VITE_API_BASE_URL` pointing at the backend.
- Log in with the local demo owner account.
- Confirm the dashboard shows the demo company, active subscription, and `BuildIQ v0.9 RC1`.
- Open `Клиенти` and review the seeded customer and property.
- Open `Проекти` and review overview, finance summary, room areas, openings, and measurements.
- Open `Пресметки` and review the completed painting calculation result.
- Open `Понуди`, review the accepted estimate, generate a PDF, and download it.
- Open `Уплати` and confirm the demo payment.
- Open `Трошоци` and confirm the demo expense.
- Confirm no browser console warnings or API errors appear during the flow.

## Automated Validation Gates

Run every gate from the repository root before handing off an RC commit:

```bash
(cd backend && ../.venv/bin/pytest)
(cd backend && ../.venv/bin/alembic heads)
(cd frontend && npm test)
(cd frontend && npm run lint)
(cd frontend && npm run build)
git diff --check
```

The provider/runtime scan must return no matches:

```bash
rg -n -i 'openai|anthropic|gemini|langchain|llamaindex' \
  backend/app backend/pyproject.toml frontend/src frontend/package.json
```

The old-brand and provider-secret-name scan must return no matches:

```bash
rg -n 'OneFiveFour|OFFMI|OPENAI_API_KEY|ANTHROPIC_API_KEY|GEMINI_API_KEY' . \
  --glob '!docs/032-release-candidate-checklist.md' \
  --glob '!frontend/node_modules/**' --glob '!frontend/dist/**' --glob '!backend/.venv/**'
rg -n '(^|[^A-Za-z0-9])sk-[A-Za-z0-9_-]{8,}' . \
  --glob '!docs/032-release-candidate-checklist.md' \
  --glob '!frontend/node_modules/**' --glob '!frontend/dist/**' --glob '!backend/.venv/**'
```

Any match must be reviewed. Prohibition text in documentation is expected for provider names, but provider imports, dependencies, endpoints, or credential values are not allowed.

## Friend/User Testing Instructions

- Ask testers to follow `docs/031-mvp-demo-flow.md` first without guidance.
- Ask them where labels, empty states, or financial terminology feel unclear.
- Ask them to create one new customer, property, project, room, calculation, estimate, payment, and expense after the seeded demo.
- Ask them not to test unsupported modules as production-ready features.
- Record friction as product feedback unless it breaks the documented MVP flow.
- Do not collect real customer financial data during RC1 testing.
