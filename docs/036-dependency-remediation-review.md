# Program 003 Dependency Remediation Review

## Verdict

All actionable dependency advisories identified at the Program 003 baseline are resolved without exclusions, forced audit remediation, or weakened CI thresholds. Python and npm audits both report zero known vulnerabilities. Application behavior remains covered by 127 backend tests and 45 frontend tests.

## Baseline advisory matrix

Severity is recorded when the originating audit supplied it. The baseline `pip-audit` JSON did not provide severity fields, so Python severity is not inferred.

| Ecosystem | Package and version | Advisory | Severity | Type and exposure | Fixed target | Decision and validation | Final status |
|---|---|---|---|---|---|---|---|
| Python | Pillow 11.3.0 | PYSEC-2026-165; CVE-2026-25990; CVE-2026-40192; CVE-2026-42309; CVE-2026-42310; CVE-2026-42311 | Not supplied | Production transitive through ReportLab; PDF/image decoder path | 12.2.0+ | Require Pillow 12.2+; PDF integrity and complete backend suite | Resolved at 12.3.0 |
| Python | pip 26.0.1 | PYSEC-2026-196; CVE-2026-3219; CVE-2026-6357 | Not supplied | Packaging tooling; install-time exposure | 26.1.2 | Recreate environment and refresh installer | Resolved at 26.1.2 |
| Python | pytest 8.4.2 | PYSEC-2026-1845 | Not supplied | Development/test only | 9.0.3 | Move to safe 9.x line; complete backend suite | Resolved at 9.1.1 |
| Python | python-dotenv 1.2.1 | CVE-2026-28684 | Not supplied | Production configuration loading | 1.2.2 | Patch minimum; configuration and startup tests | Resolved at 1.2.2 |
| Python | setuptools 58.0.4 | PYSEC-2022-43012; PYSEC-2025-49; PYSEC-2026-1918 | Not supplied | Build tooling | 78.1.1 | Recreate environment; raise build-system floor | Resolved at 83.0.0 |
| Python | Starlette 0.49.3 | PYSEC-2026-161; PYSEC-2026-248; PYSEC-2026-249; CVE-2026-48817; CVE-2026-48818 | Not supplied | Production HTTP runtime through FastAPI | 1.3.1 | Upgrade with FastAPI; auth, CORS, request, OpenAPI, and full backend tests | Resolved at 1.3.1 |
| npm | esbuild 0.21.5 | GHSA-67mh-4wv8-2f99 / npm 1102341 | Moderate | Transitive build/dev server; local development exposure | Via Vite 8.1.4 | Upgrade parent toolchain; clean install, audit, test, lint, build | Resolved; no longer in Vite 8 build path |
| npm | Vite 5.4.21 | npm 1116229, 1120784, 1120789 | High | Direct build/dev server; development exposure | 8.1.4 | Reviewed major upgrade and production assets | Resolved at 8.1.4 |
| npm | Vitest 2.1.9 | npm 1120126 | Critical | Direct test/UI server; development/CI exposure | 4.1.10 | Reviewed major upgrade and all component tests | Resolved at 4.1.10 |
| npm | `@vitest/mocker` 2.1.9 | Parent-chain finding | Moderate | Transitive test tooling | Via Vitest 4.1.10 | Upgrade Vitest; mock behavior covered by tests | Resolved |
| npm | `vite-node` 2.1.9 | Parent-chain finding | Moderate | Transitive test execution | Via Vitest 4.1.10 | Upgrade Vitest; module execution covered by tests | Resolved/removed |

Duplicate aliases emitted by the Python advisory service were counted in the baseline total but are listed once above. The retained ignored JSON reports contain the machine-readable raw evidence and are not committed because they are ephemeral audit artifacts.

## Dependency classification

- Production runtime: FastAPI, Starlette, python-dotenv, ReportLab, Pillow.
- Development/test: pytest, Vitest, `@vitest/mocker`, `vite-node`.
- Build/tooling: pip, setuptools, wheel, Vite, esbuild.
- Browser runtime libraries were not upgraded.

BuildIQ does not implement file uploads, thumbnails, user-supplied image processing, or background tasks. Those paths are not claimed as tested or exposed. Pillow remains relevant because ReportLab can use it in document rendering.

## Regression evidence

- Configuration aliases, production rejection gates, missing/default behavior, and CORS parsing pass focused tests.
- Generated PDFs retain a PDF header, EOF marker, non-trivial size, and page object; generation, metadata scoping, authorization, download, Cyrillic/font, and workflow tests pass.
- Authentication, authorization, tenancy, subscriptions, serialization, exception paths, CORS, health, OpenAPI export, and production configuration gates pass the backend suite.
- Frontend routing, authentication, tenant-aware cache behavior, API calls, mocks, CSS processing, lint, and production assets pass after Vite/Vitest upgrades.
- Route-level lazy loading reduced the entry chunk from approximately 520 kB before remediation (527.24 kB immediately after Vite 8) to 367.94 kB and 112.83 kB gzip.

## Final advisory state

| Audit | Critical | High | Moderate | Other actionable |
|---|---:|---:|---:|---:|
| `pip-audit --local` | 0 | 0 | 0 | 0 |
| `npm audit --audit-level=high` | 0 | 0 | 0 | 0 |

No residual advisory is accepted. Non-security deprecation warnings are documented in `docs/dependency-remediation-results.md` and have no advisory exception or expiry requirement.

## Rollback

Program 003 starts after `025a337`. Each dependency group is independently revertible in reverse order. The complete program can be rolled back by restoring the reviewed Program 002 commit on a new branch; do not rewrite published history. Reinstall backend dependencies in a fresh environment and use `npm ci` after any rollback so installed packages match the selected revision.
