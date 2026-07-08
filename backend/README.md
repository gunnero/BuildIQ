# BuildIQ Backend

FastAPI backend for BuildIQ.

## Scope

The backend currently includes:

- FastAPI application factory
- `/health` endpoint
- `/api/v1` router structure
- Environment-based configuration
- Basic logging setup
- PostgreSQL SQLAlchemy engine/session setup
- Alembic base configuration
- Pytest setup
- Identity and tenant foundation
- Password hashing
- JWT access tokens
- Current user and current company dependencies
- Role and permission helper structure
- Company subscription read model
- Customer and property engine
- Customer/property contact and property note endpoints
- Project and task engine
- Project status history and timeline event endpoints
- Room and measurement engine
- Room opening, measurement set, and measurement item endpoints
- Calculation engine framework
- Placeholder calculation engine registry and auditable calculation run endpoints
- Painting calculation engine
- Material engine
- Material category, manufacturer, unit, material, and consumption rule endpoints
- Procurement engine
- Supplier, supplier contact, supplier agreement, price book, price book item, project price override, and resolved price endpoints
- Estimate engine
- Estimate, estimate revision, estimate item, status, archive, and from-calculation endpoints
- Payment and expense engine
- Payment, payment allocation, expense category, expense, reversal, archive, and project financial summary endpoints
- Backend API contract stabilization
- OpenAPI tag metadata and export command
- Shared error helpers and audit helper
- Local development seed command

The backend intentionally does not include:

- Frontend implementation
- Tiles, knauf, flooring, concrete, facade, or other business modules
- Online payments or payment provider integrations
- PDF generation
- AI features
- OpenAI, Anthropic, Gemini, LangChain, LlamaIndex, or other LLM/provider SDKs

Future AI features must integrate only through Kalveri OS.

## Local Setup

From the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e './backend[dev]'
cp .env.example .env
docker compose up -d postgres
```

Create and migrate the database:

```bash
cd backend
../.venv/bin/alembic upgrade head
```

Seed initial local development data:

```bash
cd backend
../.venv/bin/buildiq-seed-dev
```

Default local seed accounts:

- HQ admin: `hq@buildiq.local`
- Demo owner: `owner@demo.buildiq.local`

Both use `ChangeMe123!` unless overridden with:

```bash
BUILDIQ_SEED_HQ_PASSWORD='new-password' BUILDIQ_SEED_OWNER_PASSWORD='new-password' ../.venv/bin/buildiq-seed-dev
```

## Run the App

```bash
cd backend
../.venv/bin/uvicorn app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Interactive API documentation:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

Export the OpenAPI contract to `docs/api/openapi.json`:

```bash
cd backend
../.venv/bin/buildiq-export-openapi
```

You can also pass a custom output path:

```bash
cd backend
../.venv/bin/buildiq-export-openapi ../docs/api/openapi.json
```

Authentication endpoints:

- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/companies/me`
- `GET /api/v1/subscription/me`

Customer and property endpoints:

- `POST /api/v1/customers`
- `GET /api/v1/customers`
- `GET /api/v1/customers/{customer_id}`
- `PATCH /api/v1/customers/{customer_id}`
- `POST /api/v1/customers/{customer_id}/archive`
- `POST /api/v1/customers/{customer_id}/contacts`
- `GET /api/v1/customers/{customer_id}/contacts`
- `POST /api/v1/properties`
- `GET /api/v1/properties`
- `GET /api/v1/properties/{property_id}`
- `PATCH /api/v1/properties/{property_id}`
- `POST /api/v1/properties/{property_id}/archive`
- `POST /api/v1/properties/{property_id}/contacts`
- `GET /api/v1/properties/{property_id}/contacts`
- `POST /api/v1/properties/{property_id}/notes`
- `GET /api/v1/properties/{property_id}/notes`

Project and task endpoints:

- `POST /api/v1/projects`
- `GET /api/v1/projects`
- `GET /api/v1/projects/{project_id}`
- `PATCH /api/v1/projects/{project_id}`
- `POST /api/v1/projects/{project_id}/archive`
- `POST /api/v1/projects/{project_id}/status`
- `GET /api/v1/projects/{project_id}/status-history`
- `GET /api/v1/projects/{project_id}/timeline`
- `POST /api/v1/projects/{project_id}/tasks`
- `GET /api/v1/projects/{project_id}/tasks`
- `GET /api/v1/tasks/{task_id}`
- `PATCH /api/v1/tasks/{task_id}`
- `POST /api/v1/tasks/{task_id}/archive`
- `POST /api/v1/tasks/{task_id}/status`

Room and measurement endpoints:

- `POST /api/v1/projects/{project_id}/rooms`
- `GET /api/v1/projects/{project_id}/rooms`
- `GET /api/v1/rooms/{room_id}`
- `PATCH /api/v1/rooms/{room_id}`
- `POST /api/v1/rooms/{room_id}/archive`
- `POST /api/v1/rooms/{room_id}/openings`
- `GET /api/v1/rooms/{room_id}/openings`
- `PATCH /api/v1/openings/{opening_id}`
- `POST /api/v1/openings/{opening_id}/archive`
- `POST /api/v1/projects/{project_id}/measurement-sets`
- `GET /api/v1/projects/{project_id}/measurement-sets`
- `GET /api/v1/measurement-sets/{measurement_set_id}`
- `POST /api/v1/measurement-sets/{measurement_set_id}/items`
- `GET /api/v1/measurement-sets/{measurement_set_id}/items`
- `PATCH /api/v1/measurement-items/{measurement_item_id}`
- `POST /api/v1/measurement-items/{measurement_item_id}/archive`

Calculation framework endpoints:

- `GET /api/v1/calculation-engines`
- `POST /api/v1/calculations/run`
- `GET /api/v1/calculations`
- `GET /api/v1/calculations/{calculation_run_id}`
- `POST /api/v1/calculations/{calculation_run_id}/archive`

Painting calculation example:

```json
{
  "engine_type": "painting",
  "project_id": "project-id",
  "room_id": "room-id",
  "input_payload": {
    "include_ceiling": true,
    "include_walls": true,
    "coats": 2,
    "primer_coats": 0,
    "paint_material_id": "material-id",
    "waste_percentage": 10,
    "labor_rate_per_m2": 120,
    "notes": "Interior repaint"
  }
}
```

Painting calculations use backend-computed room areas when `room_id` is provided. If no room is provided, a measurement set can provide `wall_area`, `ceiling_area`, or `paintable_area` measurement items in `m2`. Material costs use Procurement Engine price resolution when material IDs are supplied.

Material endpoints:

- `POST /api/v1/material-categories`
- `GET /api/v1/material-categories`
- `PATCH /api/v1/material-categories/{category_id}`
- `POST /api/v1/material-categories/{category_id}/archive`
- `POST /api/v1/material-manufacturers`
- `GET /api/v1/material-manufacturers`
- `PATCH /api/v1/material-manufacturers/{manufacturer_id}`
- `POST /api/v1/material-manufacturers/{manufacturer_id}/archive`
- `GET /api/v1/material-units`
- `POST /api/v1/material-units`
- `POST /api/v1/materials`
- `GET /api/v1/materials`
- `GET /api/v1/materials/{material_id}`
- `PATCH /api/v1/materials/{material_id}`
- `POST /api/v1/materials/{material_id}/archive`
- `POST /api/v1/material-consumption-rules`
- `GET /api/v1/material-consumption-rules`
- `GET /api/v1/materials/{material_id}/consumption-rules`
- `PATCH /api/v1/material-consumption-rules/{rule_id}`
- `POST /api/v1/material-consumption-rules/{rule_id}/archive`

Procurement endpoints:

- `POST /api/v1/suppliers`
- `GET /api/v1/suppliers`
- `GET /api/v1/suppliers/{supplier_id}`
- `PATCH /api/v1/suppliers/{supplier_id}`
- `POST /api/v1/suppliers/{supplier_id}/archive`
- `POST /api/v1/suppliers/{supplier_id}/contacts`
- `GET /api/v1/suppliers/{supplier_id}/contacts`
- `PATCH /api/v1/supplier-contacts/{contact_id}`
- `POST /api/v1/supplier-contacts/{contact_id}/archive`
- `POST /api/v1/suppliers/{supplier_id}/agreements`
- `GET /api/v1/suppliers/{supplier_id}/agreements`
- `GET /api/v1/supplier-agreements/{agreement_id}`
- `PATCH /api/v1/supplier-agreements/{agreement_id}`
- `POST /api/v1/supplier-agreements/{agreement_id}/archive`
- `POST /api/v1/price-books`
- `GET /api/v1/price-books`
- `GET /api/v1/price-books/{price_book_id}`
- `PATCH /api/v1/price-books/{price_book_id}`
- `POST /api/v1/price-books/{price_book_id}/archive`
- `POST /api/v1/price-books/{price_book_id}/items`
- `GET /api/v1/price-books/{price_book_id}/items`
- `PATCH /api/v1/price-book-items/{item_id}`
- `POST /api/v1/price-book-items/{item_id}/archive`
- `POST /api/v1/projects/{project_id}/material-price-overrides`
- `GET /api/v1/projects/{project_id}/material-price-overrides`
- `PATCH /api/v1/material-price-overrides/{override_id}`
- `POST /api/v1/material-price-overrides/{override_id}/archive`
- `GET /api/v1/materials/{material_id}/resolved-price`
- `GET /api/v1/projects/{project_id}/materials/{material_id}/resolved-price`

Estimate endpoints:

- `POST /api/v1/estimates`
- `GET /api/v1/estimates`
- `GET /api/v1/estimates/{estimate_id}`
- `PATCH /api/v1/estimates/{estimate_id}`
- `POST /api/v1/estimates/{estimate_id}/archive`
- `POST /api/v1/estimates/{estimate_id}/status`
- `POST /api/v1/estimates/from-calculation/{calculation_run_id}`
- `GET /api/v1/estimates/{estimate_id}/revisions`
- `GET /api/v1/estimate-revisions/{revision_id}`
- `POST /api/v1/estimate-revisions/{revision_id}/items`
- `GET /api/v1/estimate-revisions/{revision_id}/items`
- `PATCH /api/v1/estimate-items/{item_id}`
- `POST /api/v1/estimate-items/{item_id}/archive`

Estimate revision totals are calculated by the backend from active items. Sent and accepted revisions are immutable; changes after those statuses require a new revision workflow in a later sprint.

Payment and expense endpoints:

- `POST /api/v1/payments`
- `GET /api/v1/payments`
- `GET /api/v1/payments/{payment_id}`
- `POST /api/v1/payments/{payment_id}/reverse`
- `POST /api/v1/payments/{payment_id}/archive`
- `GET /api/v1/projects/{project_id}/financial-summary`
- `POST /api/v1/expense-categories`
- `GET /api/v1/expense-categories`
- `PATCH /api/v1/expense-categories/{category_id}`
- `POST /api/v1/expense-categories/{category_id}/archive`
- `POST /api/v1/expenses`
- `GET /api/v1/expenses`
- `GET /api/v1/expenses/{expense_id}`
- `POST /api/v1/expenses/{expense_id}/reverse`
- `POST /api/v1/expenses/{expense_id}/archive`

Payments and expenses preserve financial history. Payments are append-only after creation except reversal/archive status changes. Project financial summaries are calculated by the backend from accepted estimate totals, agreed project price, received/pending/reversed payments, and recorded/reversed expenses.

## Run Tests

```bash
cd backend
../.venv/bin/python -m pytest
```

## Alembic

Alembic is configured for PostgreSQL.

Current migration status:

- Identity and tenant foundation tables exist.
- Customer and property tables exist.
- Project and task tables exist.
- Room and measurement tables exist.
- Calculation framework tables exist.
- Painting calculation engine is implemented.
- Material catalog and material consumption rule tables exist.
- Procurement tables exist.
- Estimate tables exist.
- Payment and expense tables exist.
- API contract export is available.
- No tiles, knauf, flooring, concrete, facade, online payment, or PDF tables exist yet.

Migration commands:

```bash
cd backend
../.venv/bin/alembic heads
../.venv/bin/alembic upgrade head
```
