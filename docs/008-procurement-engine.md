# Procurement Engine

The Procurement Engine manages suppliers, stores, supplier agreements, price books, retail prices, negotiated company prices, and project price overrides.

## Purpose

Construction pricing changes over time. BuildIQ must preserve enough procurement history to explain why a material price appeared on an estimate.

## Core Concepts

### Material Catalog Boundary

The Material Engine owns material categories, manufacturers, materials, material units, and material consumption rules.

The Procurement Engine starts after a material exists. It owns supplier relationships, supplier agreements, price books, retail prices, negotiated company prices, and project price overrides.

Material records must not store supplier pricing history. Procurement records must snapshot and preserve pricing history when price books, agreements, overrides, material lists, or estimates are introduced.

### Suppliers / Stores

Suppliers are companies that sell materials.

Stores are supplier locations or branches.

Both are company-scoped in BuildIQ because each BuildIQ company may manage its own supplier relationships.

Sprint 8 represents suppliers and stores through the `suppliers` table. The `supplier_type` field distinguishes `supplier` from `store`, and a store may reference a parent supplier with `parent_supplier_id`.

### Supplier Agreements

Supplier agreements store negotiated commercial terms between a BuildIQ company and a supplier.

Agreements must preserve:

- Supplier
- Agreement number
- Start date
- End date
- Status
- Terms snapshot
- History of changes

### Price Books

Price books store material pricing for a date range.

Price books may include:

- Retail prices
- Negotiated company prices
- Supplier SKUs
- Units
- Validity periods

Sprint 8 price books use `price_type` values:

- `negotiated`
- `retail`
- `default`

### Retail Prices

Retail price is the standard supplier or store price.

Retail price history must be preserved.

### Negotiated Company Prices

Negotiated company price is the price available to one BuildIQ company through a supplier agreement or relationship.

Negotiated prices must not overwrite retail prices.

### Project Price Overrides

Project price overrides are project-specific prices approved for a material.

Overrides must preserve:

- Project
- Material
- Unit price
- Reason
- Author
- Creation date
- Supersession date when replaced

Sprint 8 project material price overrides store `created_by_user_id`, `reason`, validity dates, currency, and notes. Overrides are archived rather than hard-deleted.

## Price Resolution

Backend price resolution order:

1. Active project price override
2. Active negotiated company price
3. Active retail price
4. Manual backend-approved price

The selected source must be written to the material list item or estimate item.

Sprint 8 exposes resolved price reads before material lists and estimates exist:

- `GET /api/v1/materials/{material_id}/resolved-price`
- `GET /api/v1/projects/{project_id}/materials/{material_id}/resolved-price`

The response source is one of:

- `project_override`
- `negotiated_price_book`
- `retail_price_book`
- `none`

For price book matches, `source_id` is the selected price book item ID.

## History Rules

- Supplier agreements must not be hard-deleted.
- Price books must not be hard-deleted.
- Price book items must preserve validity windows.
- Overrides must be superseded rather than overwritten.
- Estimate items must snapshot the price used at the time of revision creation.

## Procurement Workflow

1. Company creates or imports supplier.
2. Company adds stores when needed.
3. Company records supplier agreement.
4. Company creates price book.
5. Company adds retail and negotiated prices.
6. Project uses calculated or manual material list.
7. Backend resolves material prices.
8. Estimate revision snapshots selected prices.

## V1 Boundary

V1 may start with manual price book management.

No supplier API integrations are required for V1.

Future integrations belong behind the Integration Engine.
