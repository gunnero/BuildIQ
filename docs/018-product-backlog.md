# Product Backlog

This backlog translates BuildIQ Blueprint v1.0 into implementation-ready product areas. It is not an implementation plan and does not create backend, frontend, or database code.

## Priority Legend

- P0: Required for V1 foundation
- P1: Required for complete V1 workflow
- P2: Useful after core V1 workflow is stable
- Future: Post-V1 or dependent on later strategy

## P0 Foundation

- Create backend application shell.
- Create frontend application shell.
- Configure PostgreSQL connection.
- Configure Alembic.
- Implement JWT authentication.
- Implement company scope middleware or dependency.
- Implement employee, role, and permission model.
- Implement audit log foundation.
- Implement Macedonian validation message pattern.

## P0 BuildIQ Kernel

- Add company model.
- Add feature flag model.
- Add audit log model.
- Add shared status and archival conventions.
- Add MKD currency conventions.
- Add metric unit conventions.

## P1 Customer Engine

- Customer CRUD.
- Property CRUD.
- Customer profile.
- Customer project history.
- Customer payment summary.

## P1 Project Engine

- Project CRUD.
- Project status workflow.
- Task management.
- Room management.
- Project summary.
- Project archival.

## P1 Measurement Engine

- Room measurement forms.
- Measurement snapshots.
- Opening area support.
- Metric unit validation.

## P1 Calculation Engine

- Painting calculator.
- Tile calculator.
- Knauf calculator.
- Flooring calculator.
- Calculation run snapshots.
- Material list generation from calculation results.

## P1 Material Engine

- Material catalog.
- Material list review.
- Manual material item entry.
- Material units.
- Material history.

## P1 Procurement Engine

- Supplier CRUD.
- Store CRUD.
- Supplier agreements.
- Price books.
- Retail prices.
- Negotiated company prices.
- Project price overrides.
- Price source snapshots.

## P1 Estimate Engine

- Estimate drafts.
- Estimate revisions.
- Estimate line items.
- Estimate acceptance.
- Project agreed price update from accepted revision.
- Estimate PDF source snapshot.

## P1 Financial Engine

- Payment recording.
- Payment history.
- Expense recording.
- Expense history.
- Total paid calculation.
- Outstanding balance calculation.
- Payment status calculation.
- Voiding payments and expenses.

## P1 Document Engine

- Macedonian PDF quote generation.
- PDF storage metadata.
- Estimate revision to PDF link.
- PDF authorization.

## P1 Reporting Engine

- Dashboard summary.
- Outstanding balance summary.
- Payment summary.
- Expense summary.
- Project status summary.

## P1 Subscription Engine

- Company subscription status.
- Manual subscription payments by bank transfer.
- HQ review workflow.
- Subscription audit logs.
- Feature flags linked to subscription state.

## P1 BuildIQ HQ

- HQ authentication boundary.
- Company list.
- Company subscription management.
- Manual payment review.
- Feature flag management.
- Audit log viewer.

## P2 Improvements

- Advanced project reports.
- Supplier price import.
- Estimate templates.
- PDF theme settings.
- Project profitability reporting.
- Customer portal exploration.

## Future Integrations

- Online payment provider abstraction.
- Supplier integrations behind the Integration Engine.
- Accounting exports.
- Future AI workflows through Kalveri OS only.

## Explicitly Out of Scope for V1

- Direct OpenAI integration.
- Direct Anthropic integration.
- Direct Gemini integration.
- Direct LLM provider integration.
- AI chat.
- AI estimate generation.
- Provider SDKs.
- Backend implementation in this documentation task.
- Frontend implementation in this documentation task.
- Database migrations in this documentation task.
