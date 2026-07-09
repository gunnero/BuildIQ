# BuildIQ v0.9 RC1 Technical and Product Audit

Date: 2026-07-09  
Branch audited: `develop`  
Baseline revision: `337e59d9ad7aab7f5ae6c4c485630bdecf81b0b5`  
Scope: documentation, backend, frontend, local product flow, production deployment, and security

## Executive Summary

BuildIQ v0.9 RC1 has a coherent backend-owned domain model, consistent company scoping on the reviewed business APIs, a usable Macedonian demo flow, tenant-isolated PDF metadata/download paths, and broad automated happy-path coverage. The local audit confirmed that the seeded populated and empty companies remain isolated during a normal same-tab logout/login flow. No direct AI/provider SDK, provider credential, committed production secret, raw-SQL injection sink, arbitrary outbound request surface, unsafe upload/parser surface, or runtime hard-delete endpoint was found.

The release candidate is suitable for controlled local or isolated RC testing, but it is not ready for a production go-live. The release-blocking work is concentrated rather than architectural: backend roles and permissions are modeled but are not enforced by any route; production startup does not reject the known development JWT secret or an empty replacement; cross-tab browser token changes can mix stale tenant UI state with another tenant's token; the project screen can retain child selections across a project switch; financial values are persisted as binary floating-point numbers; and the web01 runbook lacks a workable privilege model, a database-backup gate, and a single deterministic reverse-proxy path.

This pass deliberately does not redesign architecture, change tenant-isolation rules, add major features, add AI/provider SDKs, deploy, or make the high-risk state/session/database/deployment changes above. Safe documentation, copy, UI-state, test, and deterministic-build corrections are listed under the improvement pass and are kept separate from the next-sprint blockers.

## Audit Method

- Reviewed every tracked documentation source named in the mission, all backend and frontend runtime/configuration files, migrations, tests, deployment scripts, env examples, and the exported OpenAPI contract.
- Ran the application locally against a disposable SQLite database because Docker is unavailable on this workstation. PostgreSQL remains the intended production database and is covered by the backend test/migration and deployment review, not by this visual-only fallback.
- Captured the current login, validation, dashboard, customers, estimates, mobile, and empty-company states in the in-app browser.
- Tested a same-tab switch from the populated demo company to the intentionally empty Hristijan company and confirmed that old offers were not shown after the switch.
- Ran a repository-wide security scan at the baseline revision with an explicit threat model, file-review worklist, candidate receipts, validation, and attack-path analysis. The generated security report is an audit input; this document remains the product/technical release decision.

## Release Decision

**RC1 decision: conditional pass for controlled RC testing; fail for production go-live.**

The current application can support the documented friend/test-user walkthrough on isolated demo data. Production deployment should wait until all High items marked as go-live blockers are resolved and the web01 preflight, backup/restore, configuration validation, and smoke tests are executed on the actual host.

## Critical Issues

No confirmed Critical issue was found in the audited revision.

The audit found no unauthenticated remote-code-execution path, universal authentication bypass, known production secret, platform-wide tenant extraction path, or arbitrary server file read/write primitive. This statement is limited to the repository and local behavior reviewed; it is not a claim about the uninspected live host or network configuration.

## High Priority Issues

### H1. Role and permission enforcement is not connected to API routes

`backend/app/services/authorization.py` implements `require_permission()`, but no route uses it. The Blueprint requires permissions for customer, project, measurement, estimate, payment, expense, supplier, price-book, subscription, feature-flag, and audit actions (`docs/014-security.md`). At present, any active user in a company can call every authenticated company route, including financial reversals, estimate status changes, PDF generation, procurement changes, and archives.

This is a same-tenant privilege-control gap rather than a confirmed cross-tenant leak. It is a production blocker because the role model is exposed in current-user responses and seeded data, so operators can reasonably assume it is enforced when it is not.

Recommended action: define the RC1 permission matrix, apply backend dependencies to every sensitive route, add owner/manager/worker negative tests, and keep frontend visibility strictly secondary to backend enforcement.

### H2. Production configuration does not fail closed

`backend/app/core/config.py` defaults to the public development JWT secret `change-me-in-local-development-secret-key` and does not validate production settings. `backend/.env.production.example` leaves the replacement value empty, while the deployment guide relies on an operator replacing it correctly. A missing, empty, or incorrectly loaded production env can therefore start with a known or unusable signing key instead of refusing startup. The same fail-open configuration accepts `BUILDIQ_ENV=production` with `BUILDIQ_DEBUG=true`, which allows unauthenticated 500 responses to expose tracebacks and filesystem paths. Strict production CORS likewise depends entirely on the env override; defaults include local Vite origins and the temporary domain.

Recommended action: when `BUILDIQ_ENV=production`, reject the development/empty/short secret, debug mode, non-HTTPS or wildcard origins, relative storage paths, and development database credentials. Add focused config tests and a documented secret-generation/verification command.

### H3. Cross-tab token replacement can mix tenant contexts

`frontend/src/auth/AuthContext.tsx` hydrates user/company/subscription and query cache from one token, while `frontend/src/api/client.ts` rereads the shared local-storage token on every request. There is no `storage` event listener and query keys are not tenant-scoped. If another tab logs into a different account, the first tab can continue showing the prior tenant's cached data while later reads or mutations carry the new tenant's token.

Same-tab logout/login is correctly cleared and was verified locally. The missing case is an external or second-tab token change.

Recommended action: make the authenticated session the single request-token source, listen for token storage changes, atomically clear user/company/query state before accepting a replacement token, and add a two-tab regression test.

### H4. Project child selections survive a project switch

`frontend/src/pages/ProjectsPage.tsx` changes `selectedProjectId` without clearing selected room, opening, measurement-set, measurement-item, and related form state. Detail queries and mutations can therefore continue operating on an entity from the previous project while the screen shows the new project.

This is a same-tenant cross-project corruption risk. It was not changed during this pass because the correct fix must treat project selection as one state transition and reset every descendant consistently.

Recommended action: implement and test an explicit project-selection reset covering rooms, openings, measurement sets/items, tasks, tabs, and edit forms across two projects.

### H5. Financial and price data use binary floating-point storage

Project agreed prices, estimate prices/totals, procurement prices, payments, allocations, and expenses use SQLAlchemy `Float` and Python/JSON `float`. Binary floating point is not a safe authoritative representation for money and can produce rounding drift across revisions, allocations, summaries, PDFs, and reconciliation. The long decimal values visible in the estimate UI are already a product symptom.

Recommended action: plan a reviewed additive migration to fixed-precision `NUMERIC`, define currency scale and rounding rules, migrate/verify existing values, update schemas/services, and add boundary/reconciliation tests. Do not patch this ad hoc in RC1.

### H5a. Non-finite numeric values can poison authoritative data

Several accepted `float` inputs only reject values below or equal to zero. `Infinity` therefore passes material, procurement, estimate-item, payment, and expense validation, can be committed, and then propagates into totals, price resolution, financial summaries, or response serialization. This is a concrete integrity and availability path for an authenticated company user, distinct from the longer-term fixed-precision storage decision.

Recommended action: add finite-number guards at the schema/service boundary, reject non-finite JSON values consistently, add regression tests for every money/quantity family, and plan the fixed-precision migration separately.

### H6. web01 deployment flow has incompatible privilege and web-server assumptions

The runbook creates `buildiq` as a system/service user and later tells that account to run a helper that calls privileged `sudo` operations. No sudoers policy or privileged-operator handoff is defined. The prerequisites unconditionally install nginx and nginx Certbot while Apache is also presented as supported; the helper will choose nginx whenever its unit exists, and rollback always reloads nginx.

Recommended action: choose and verify one active web server, run deployment from a named privileged operator while executing application build steps as `buildiq`, or define a narrowly scoped sudo policy. Parameterize validation/reload/rollback around the chosen server.

### H7. There is no database backup and restore gate before migrations

The helper runs Alembic as a normal deploy step. The checklist does not require a fresh backup, recorded backup location, retention owner, or restore test, while rollback correctly notes that migrations are not automatically reversible.

Recommended action: make a successful PostgreSQL backup plus a documented restore check an explicit stop/go gate before migrations. Record the deployed and target revisions, migration heads, backup identifier, and rollback owner.

### H8. Documentation can direct implementers toward unsafe hard deletes and false readiness

`docs/006-api-design.md` still advertises `DELETE` routes for important business records even though the constitution and current API require archive/reversal/history behavior. README and changelog say deployment is prepared while the RC checklist says production hardening is not included and the RC is not for production.

Recommended action: mark target-state/historical documents clearly, make exported OpenAPI plus current backend/frontend READMEs authoritative for RC1, and use one release statement: controlled RC testing only until production-hardening gates pass.

### H9. The documented demo seed left two public test-owner passwords unchanged (resolved)

The baseline RC1 seed command overrode only the HQ and primary owner passwords. The seed also created the Aleksandar and Hristijan test-owner accounts with a shared public default, and rerunning the seed did not rotate existing hashes. Security Sprint 1 removes that default, requires four unique supplied passwords, rotates existing seeded hashes when supplied, and refuses production seeding unless explicitly overridden.

Recommended action: make every seeded credential mandatory and unique for a demo environment, refuse the seed command when `BUILDIQ_ENV=production`, and add a post-seed disable/delete/rotation step before any real-user test.

### H10. Financial state machines accept client-selected historical states

Estimate status transitions can downgrade a sent or accepted revision back to an editable state, allowing price-bearing items to change without a new revision. Payment and expense creation also accept a pre-reversed state without a reversal reason or reversal actor. These are distinct from the missing permission checks: even a permitted caller can create or unlock financial history that should only be produced by the dedicated state-transition workflow.

Recommended action: make server-side state transitions monotonic/explicit, reject `reversed` on create, require reversal reasons and actor metadata, and add immutable-revision/financial-history regression tests.

## Medium Priority Issues

### M1. Sensitive mutation audit coverage is incomplete

Audit records exist for successful login and selected customer, property, project, estimate, payment, and expense actions. Large mutation surfaces in tasks, rooms, measurements, materials, procurement, estimate items/PDF generation, and many updates/archives do not write audit events. Audit rows are append-only by convention but the database model does not itself prevent privileged modification.

Recommended action: define auditable actions by domain, route all writes through the shared audit helper, capture before/after state without secrets, and test actor/company/target bindings.

### M2. Login abuse protection is operationally undefined

The public login endpoint performs an intentionally expensive PBKDF2 check but has no application rate limit, lockout/backoff, or failed-login audit. The deployment examples do not add reverse-proxy rate limiting.

Recommended action: add an abuse-control design that avoids user enumeration, records safe failure metadata, and places rate limits at the proxy and/or application boundary.

### M3. Session bootstrap treats every failure as expiration

The frontend loads `/auth/me`, `/companies/me`, and `/subscription/me` with `Promise.all`. A network error or 5xx clears a valid session and displays “session expired,” causing avoidable logout during backend restarts or transient outages.

Recommended action: clear auth only on authenticated 401/invalid-session results; preserve the token and offer retry for transient failures.

### M4. Estimate loading failures are rendered as empty or valid financial state

Revision and item query loading/error states are discarded on the estimate screen. A failure can appear as “no revisions,” “no items,” or missing totals rather than an explicit error. This can mislead users reviewing commercial data.

Recommended action: make loading, error, and empty states mutually exclusive and add focused tests.

### M5. Invalid archive statuses are offered in normal status selectors

The project and task selectors include `archived`, but the backend rejects that transition and requires the dedicated archive endpoints. The UI therefore presents an action that cannot succeed.

Recommended action: remove `archived` from both selectors and retain the explicit archive action.

### M6. Mutation pending states are inconsistent

Several estimate, calculation, payment, expense, reversal, archive, and status buttons remain enabled during mutation. Rapid repeat clicks can create duplicate requests or confusing state.

Recommended action: disable affected controls while pending, show a Macedonian progress label, and test repeat-click behavior.

### M7. PDF generation can orphan files and lacks quota/retention controls

The PDF file is written before the document metadata transaction commits. A later database failure can leave an orphan file. Any authenticated company user can repeatedly generate new PDFs, and no quota, retention, deduplication, or cleanup policy is defined. Path containment and company-scoped downloads are correctly implemented.

Recommended action: add transaction-aware cleanup, permission checks, rate/size limits, and a retention policy without moving rendering or totals into the frontend.

### M8. API errors are only partly standardized

Domain helpers return Macedonian messages, while framework validation and unhandled failures use separate structures. There is no global request/error correlation layer, and the frontend collapses array validation details to one generic message.

Recommended action: define a stable error envelope with request ID, safe code, Macedonian user message, and server-only diagnostics.

### M9. Documentation source-of-truth and vocabulary drift

Several Blueprint documents still say implementation has not begun, duplicate numeric prefixes obscure order, target V1 modules are mixed with current RC1 scope, and API/financial/version terms conflict with the implemented contract. PDF docs also lag the implemented frontend.

Recommended action: add a documentation index with `current`, `target-state`, `historical`, and `superseded` labels. Treat `docs/api/openapi.json`, current READMEs, changelog, RC checklist, demo flow, user guide, and deployment guide as the RC1 operational set.

### M10. Production service hardening is incomplete

The systemd example lacks a restrictive `UMask`, `NoNewPrivileges`, `PrivateTmp`, filesystem protections, and resource limits. Proxy examples lack a full security-header and rate-limit policy. These omissions align with the checklist statement that production hardening is not included.

Recommended action: harden and verify the actual web01 unit and proxy after discovering the host's real OS, service user, active web server, port use, DNS, and existing vhosts.

### M11. PDF Cyrillic support depends on a host font and silently falls back

The PDF renderer searches common DejaVu/Arial paths and silently falls back to Helvetica. Helvetica does not provide the required Macedonian Cyrillic coverage, so a minimal server image can produce unreadable or missing glyphs without failing the request.

This pass adds `fonts-dejavu-core` to the web01 prerequisites. A later hardening step should make the Unicode font an explicit packaged/runtime dependency and fail generation clearly when it is unavailable.

## Low Priority Polish

- The dashboard always shows first-use onboarding copy, even for the populated demo company.
- Financial UI surfaces display raw `MKD` and inconsistent decimal precision despite the Macedonian display contract using `ден.`.
- Payment vocabulary conflicts between `Уплати` / `Плаќања`, `Кеш` / `Готовина`, and `Банкарски трансфер` / `Банка` across specifications and implementation.
- Some enum and event fallbacks expose raw backend English values or UUIDs.
- The mobile layout places the entire navigation stack before page content; at 390 px the user must scroll past all modules before reaching the current task.
- Dynamic messages lack consistent `aria-live`/alert semantics, login errors are not programmatically linked to inputs, and estimate row selection is mouse-oriented.
- The frontend production build is successful but produces one approximately 520 kB minified JavaScript chunk because all pages are eagerly imported.
- Runtime/package versions still say `0.1.0` while release documentation says `0.9.0-rc1`; a single version policy is needed.
- The generated PDF record list exists only in component memory; reloading cannot rediscover already-generated documents without a backend list endpoint.

## Security Findings

| Severity | Finding | Current control | Required action |
| --- | --- | --- | --- |
| High | API permission helper is unused | Authentication and company isolation | Enforce route-level permission matrix and negative tests |
| High | Production can start with known/empty signing secret | Production env example and operator instructions | Fail startup on unsafe production config |
| High | Production debug mode is accepted and leaks traceback/path details on 500s | `debug` is operator-controlled with no production guard | Reject debug in production and add safe error-response tests |
| High | Demo seed leaves known test-owner credentials active | Only HQ/owner overrides are documented | Require/rotate all seed passwords and refuse production seeding |
| High | Estimate/payment/expense state can be client-selected outside the transition workflow | Create/status paths do not enforce historical invariants | Enforce monotonic transitions, reversal reasons, and immutable revision history |
| High | Cross-tab token/cache desynchronization | Same-tab cache clearing | Synchronize storage changes and atomically reset session/cache |
| High | Non-finite numeric inputs poison totals and responses | Positive/non-negative checks only | Reject non-finite values at schema/service boundaries and add regression tests |
| Medium | Login has no repository-defined abuse control | Generic 401 and expensive password hash | Add rate/backoff policy and failed-attempt telemetry |
| Medium | Audit coverage is partial | Shared audit helper and selected events | Cover every sensitive mutation with actor/company/target evidence |
| Medium | Repeated PDF generation can exhaust storage | Authenticated route and path containment | Permission, rate/quota, retention, and orphan cleanup |
| Medium | Local-storage token amplifies any same-origin script compromise | React escaping; no raw HTML sink found | Keep CSP/dependency review and consider a future session-storage strategy |
| Low | OpenAPI/docs and version metadata are public by default | No debug trace in production when configured correctly | Decide and document production exposure; add proxy security headers |

Positive security controls confirmed:

- JWT decoding restricts the configured algorithm and verifies expiry.
- Every authenticated request reloads an active user and confirms the token company matches the live user company.
- Reviewed object lookups use company scope; foreign tenant misses return the same not-found behavior.
- PDF document metadata lookup is company-scoped, stored paths are relative, and resolved paths must remain below `BUILDIQ_STORAGE_PATH`.
- User-controlled PDF text is XML-escaped before ReportLab rendering.
- Runtime business APIs archive or reverse important records rather than exposing hard-delete routes.
- React uses ordinary text rendering and no `dangerouslySetInnerHTML` sink was found.
- Same-tab login, logout, and 401 handling remove the query cache and token.
- No direct provider SDK/import/API endpoint or provider credential was found.

## UX Findings

### Flow health

1. **Login — healthy with accessibility polish needed.** Macedonian copy and client-side validation are clear; pending state is present. Errors need input associations and live-region semantics.
2. **Authenticated dashboard — visually consistent but content-light.** Identity/company/subscription are clear. Static onboarding copy is misleading for populated companies and there are no backend-backed operational summaries.
3. **Customers/properties — functional but form-heavy.** Labels and API-backed data are clear. Creation forms dominate the viewport before the user sees existing records.
4. **Estimates/PDF — functional with state-integrity risk.** Backend totals and PDF actions are correctly owned by the backend. Loading errors can look empty, numbers expose excessive precision, and generated-document history does not survive reload.
5. **Account switch/empty company — healthy in the tested same-tab path.** The populated company's offer disappeared after login as the empty company. Cross-tab changes remain unsafe.
6. **Mobile — technically reflows without horizontal overflow but task access is poor.** At 390 px the full navigation precedes the page, consuming most of the first screen.

Accessibility evidence is limited to code inspection, DOM semantics, keyboard-relevant controls, and screenshots. This audit does not claim WCAG conformance; screen-reader behavior, focus order, contrast ratios, zoom, and keyboard completion still require dedicated testing.

## Backend Findings

Strengths:

- Consistent FastAPI router/service/model separation and backend-owned business calculations.
- Representative tenant-scoping tests cover detail/list and PDF paths.
- Explicit archive, reversal, revision, status-history, and timeline patterns preserve business history.
- Deterministic calculation registry and stored input/output evidence.
- PDF formatting consumes backend revision totals rather than recalculating in the renderer.
- Alembic has one linear head and migrations run successfully against the disposable audit database.

Gaps:

- Permission enforcement is not applied.
- Production config has no fail-safe validation.
- Money uses binary floating point.
- Audit coverage is incomplete.
- Public login has no abuse controls.
- PDF write/metadata commit is not failure-atomic and no retention policy exists.
- Error envelopes and correlation are inconsistent.
- Database foreign keys ensure existence but not every same-company relationship; application checks remain the only tenant relation control.

## Frontend Findings

Strengths:

- No frontend construction, area, pricing, total, balance, or profit calculations were found.
- Session data, company, subscription, and all domain values come from backend responses.
- Same-tab query cache clearing is implemented and tested.
- UI and validation copy are predominantly Macedonian.
- Forms are generally labelled, tables use overflow containers, and no raw HTML sink is present.

Gaps:

- Cross-tab token/session/cache mismatch.
- Project descendant selection persistence.
- Transient session failures force logout.
- Estimate loading/error/empty states overlap.
- Several mutations lack pending locks.
- Currency/status vocabulary and formatting drift.
- Mobile navigation precedes content instead of collapsing.
- Accessibility state announcements and keyboard affordances are incomplete.

## Deployment Findings

Confirmed good assumptions:

- Uvicorn is documented on loopback behind TLS termination.
- The production origin example is a single HTTPS domain.
- PDF storage is outside the repository, owned by the service user, and not directly mapped as public static content.
- Real env files and generated PDFs are ignored and documented as uncommitted.
- Git pulls are fast-forward-only and the helper rejects a dirty tree by default.

Go-live blockers:

- No actual web01 preflight verifies OS, active web server, service user/group, Node/Python versions, port 8000, DNS, vhosts, storage, or PostgreSQL connectivity.
- Service-user and sudo assumptions conflict.
- nginx and Apache paths conflict.
- Frontend helper can reuse stale `node_modules` instead of running deterministic `npm ci`.
- No database backup/restore gate precedes migrations.
- Production secret/config validation is advisory rather than enforced.
- systemd/proxy hardening is incomplete.
- Rollback is web-server-specific and cannot reverse schema changes without a separate backup-based plan.

## Safe Improvement Pass

The following categories are authorized for this RC1 pass and do not change architecture or tenant rules:

- Mark unsafe/stale API planning docs as non-authoritative for RC1.
- Link the current PDF, demo, release, deployment, user-guide, changelog, audit, and OpenAPI documents from README.
- Add the exact automated RC validation and forbidden-term scans to the release checklist.
- Make the production frontend build deterministic with `npm ci` on every run.
- Install the documented DejaVu Unicode font package required by Macedonian PDFs.
- Clarify controlled-RC versus production-ready wording.
- Fix copy/paste path mistakes in the demo flow and add SSL renewal verification.
- Remove impossible `archived` options from normal project/task status selectors and add focused coverage.
- Replace the populated-dashboard-specific first-use assertion with neutral next-step copy if it can be tested without adding dashboard queries.

State/session rewrites, permission enforcement, financial type migrations, deployment privilege changes, backup automation, and API additions are deliberately deferred to the recommended sprint.

## Recommended Next Sprint

1. **Permission and production-config gate.** Define the permission matrix, apply it to sensitive routes, reject unsafe production secrets/debug/CORS/storage/database values, and add negative tests.
2. **Session and state integrity.** Fix cross-tab token synchronization, transient bootstrap errors, and project descendant resets with focused regression tests.
3. **Financial precision plan.** Approve fixed-precision money rules and an additive, verified migration plan; do not mix this with unrelated UI work.
4. **Audit and abuse controls.** Complete sensitive mutation audit coverage, failed-login telemetry, and a proxy/application rate-limit design.
5. **Deployment contract.** Run a read-only web01 discovery, choose nginx or Apache, define operator/service-user boundaries, add backup/restore gates, harden systemd/proxy settings, and rehearse rollback.
6. **Documentation source of truth.** Publish a docs index, label target/historical files, align financial/API/version vocabulary, and regenerate user-facing artifacts.
7. **Final RC2 validation.** Run backend/frontend tests, lint, build, migration-head check, OpenAPI export/diff, provider/secret/brand scans, security regression checks, and an authenticated web01 smoke test including PDF generation/download and two-tenant isolation.

## Security Sprint 1 Status

Security Sprint 1 is implemented in `docs/035-security-sprint-1.md`. The RC1 permission matrix is now enforced at the backend authenticated-company boundary, unsafe production configuration fails closed during settings validation, demo seeding requires unique supplied credentials and refuses production by default, and inactive subscriptions cannot access business APIs. Follow-up work remains for finer per-action policy review, audit coverage, and deployment-host verification.

## Validation Record

Baseline observations before safe fixes:

- Backend test suite: passed.
- Frontend tests: 45 passed.
- Frontend lint: passed.
- Frontend build: passed with a chunk-size warning.
- Local migrations: upgraded through `20260708_0010` on the disposable audit database.
- Local product flow: login, validation, populated tenant, empty tenant, and mobile states captured successfully.

Final validation: backend pytest passed; frontend tests 45/45 passed; frontend lint passed; frontend build passed with the existing 520.15 kB chunk warning; `git diff --check` passed; the provider/secret/old-brand scan was clean after excluding the checklist's intentional scan-pattern literals and lockfile metadata. The exact raw grep is expected to match those documented scan patterns and task identifiers, not committed credentials or provider integrations.
