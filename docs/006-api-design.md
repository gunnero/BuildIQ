# API Design

API route names must be English.

This document defines the planned V1 REST API shape. Routes will be implemented later in FastAPI.

## Base Path

All V1 routes should use:

`/api/v1`

## Authentication

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

## Companies

- `GET /api/v1/companies/current`
- `PATCH /api/v1/companies/current`

## Users / Employees

- `GET /api/v1/users`
- `POST /api/v1/users`
- `GET /api/v1/users/{user_id}`
- `PATCH /api/v1/users/{user_id}`
- `DELETE /api/v1/users/{user_id}`

## Customers

- `GET /api/v1/customers`
- `POST /api/v1/customers`
- `GET /api/v1/customers/{customer_id}`
- `PATCH /api/v1/customers/{customer_id}`
- `DELETE /api/v1/customers/{customer_id}`

## Projects

- `GET /api/v1/projects`
- `POST /api/v1/projects`
- `GET /api/v1/projects/{project_id}`
- `PATCH /api/v1/projects/{project_id}`
- `DELETE /api/v1/projects/{project_id}`
- `GET /api/v1/projects/{project_id}/summary`

## Rooms

- `GET /api/v1/projects/{project_id}/rooms`
- `POST /api/v1/projects/{project_id}/rooms`
- `GET /api/v1/rooms/{room_id}`
- `PATCH /api/v1/rooms/{room_id}`
- `DELETE /api/v1/rooms/{room_id}`

## Measurements

- `GET /api/v1/rooms/{room_id}/measurements`
- `POST /api/v1/rooms/{room_id}/measurements`
- `GET /api/v1/measurements/{measurement_id}`
- `PATCH /api/v1/measurements/{measurement_id}`
- `DELETE /api/v1/measurements/{measurement_id}`

## Calculations

- `POST /api/v1/projects/{project_id}/calculations/painting`
- `POST /api/v1/projects/{project_id}/calculations/tile`
- `POST /api/v1/projects/{project_id}/calculations/knauf`
- `POST /api/v1/projects/{project_id}/calculations/flooring`
- `GET /api/v1/projects/{project_id}/calculations`
- `GET /api/v1/calculations/{calculation_run_id}`

## Material List

- `GET /api/v1/projects/{project_id}/materials`
- `POST /api/v1/projects/{project_id}/materials`
- `PATCH /api/v1/materials/{material_item_id}`
- `DELETE /api/v1/materials/{material_item_id}`

## Estimates / Offers

- `GET /api/v1/projects/{project_id}/estimates`
- `POST /api/v1/projects/{project_id}/estimates`
- `GET /api/v1/estimates/{estimate_id}`
- `PATCH /api/v1/estimates/{estimate_id}`
- `DELETE /api/v1/estimates/{estimate_id}`
- `POST /api/v1/estimates/{estimate_id}/approve`

## Payments

- `GET /api/v1/projects/{project_id}/payments`
- `POST /api/v1/projects/{project_id}/payments`
- `GET /api/v1/payments/{payment_id}`
- `PATCH /api/v1/payments/{payment_id}`
- `DELETE /api/v1/payments/{payment_id}`

## Expenses

- `GET /api/v1/projects/{project_id}/expenses`
- `POST /api/v1/projects/{project_id}/expenses`
- `GET /api/v1/expenses/{expense_id}`
- `PATCH /api/v1/expenses/{expense_id}`
- `DELETE /api/v1/expenses/{expense_id}`

## Dashboard

- `GET /api/v1/dashboard/summary`
- `GET /api/v1/dashboard/payments`
- `GET /api/v1/dashboard/expenses`

## PDF Quote Generation

- `POST /api/v1/estimates/{estimate_id}/pdf`
- `GET /api/v1/estimates/{estimate_id}/pdf`

PDF output must be Macedonian.

## Validation Language

Request and response field names are English. User-facing validation messages returned by the API must be Macedonian.

## AI Boundary

BuildIQ must never call OpenAI, Anthropic, Gemini, or any LLM provider directly. Future AI features must integrate only through Kalveri OS. V1 has no AI routes.
