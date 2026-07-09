# PDF System

BuildIQ generates quote and offer PDFs in the backend from stored business data.

## Current RC1 Scope

Sprint 20 introduced the backend PDF system, and Sprint 21 added the current estimate PDF frontend flow.

Implemented:

- Macedonian PDF offer generation from an estimate and selected estimate revision.
- Company-scoped `EstimateDocument` metadata records.
- Local PDF storage under `BUILDIQ_STORAGE_PATH`.
- Tenant-isolated metadata and download endpoints.
- PDF download responses with `application/pdf`.
- Frontend PDF generation and download actions on estimate detail.
- Frontend display of document metadata returned by the generation request.

Not implemented:

- A backend list endpoint for rediscovering previously generated documents after a page reload.
- Invoices.
- Online payment documents.
- External document storage providers.
- AI-generated quote text.

## Language Rules

- All visible PDF text must be Macedonian.
- API routes, database tables, code, and documentation remain English.
- Validation messages returned by PDF endpoints must be Macedonian.

## Data Source Rules

PDF generation must use backend estimate data only:

- Company information.
- Customer information.
- Property and project information.
- Estimate status.
- Selected revision number.
- Active estimate revision items.
- Backend-owned revision totals.
- Notes from the revision or estimate when available.
- Generated timestamp.

The PDF renderer must not calculate estimate totals. It receives totals from the backend Estimate Engine and formats those values in the document.

## Storage

Generated PDF files are written below `BUILDIQ_STORAGE_PATH`.

The default local path is the repository `storage/` directory. Generated files must not be committed.

Stored metadata includes:

- `company_id`
- `estimate_id`
- `revision_id`
- `document_type`
- `file_path`
- `generated_by_user_id`
- `generated_at`
- `archived_at`

The stored `file_path` is relative to the configured storage root.

## API Endpoints

- `POST /api/v1/estimates/{estimate_id}/pdf`
- `GET /api/v1/estimate-documents/{document_id}`
- `GET /api/v1/estimate-documents/{document_id}/download`

`POST /api/v1/estimates/{estimate_id}/pdf` accepts an optional `revision_id`. If no revision is provided, the latest active estimate revision is used.

## Access Rules

- Users can only generate PDFs for estimates in their current company.
- Users can only read or download PDF document metadata for their current company.
- Archived estimates cannot generate new PDFs.
- Draft, sent, accepted, and rejected estimates can generate PDFs.
- Missing generated files return a not found response.

## Determinism

PDF output is generated from stored estimate data, selected revision data, backend-owned totals, and the recorded generation timestamp.

No external provider, AI service, frontend calculation, or live price lookup is used during PDF rendering.
