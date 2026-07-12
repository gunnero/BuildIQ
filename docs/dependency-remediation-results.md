# Dependency Remediation Results

## Baseline

Program 003 started from professionalization commit `025a337` on 13 July 2026. The local environment used Python 3.9.6, pip 26.0.1, setuptools 58.0.4, Node 20.20.2, and npm 10.8.2. The frontend lockfile SHA-256 was `d61e75f2302f42416bcf9636ca5f1c2517ec7cc12aff3474785a31dbae38ee91`.

Baseline functional validation was green: 127 backend tests and 45 frontend tests passed; ESLint and the production build passed. `pip check` reported no broken requirements. The production build emitted one warning for a JavaScript entry chunk of approximately 520 kB.

Baseline audits reported:

- Python: 24 advisory records affecting Pillow 11.3.0, pip 26.0.1, pytest 8.4.2, python-dotenv 1.2.1, setuptools 58.0.4, and Starlette 0.49.3.
- npm: five advisories across Vite, Vitest, esbuild, `@vitest/mocker`, and `vite-node`: three moderate, one high, and one critical.

The complete installed-package inventory and machine-specific paths were intentionally not committed. Package names and relevant versions are recorded in the remediation tables instead.

## Python tooling refresh

The ignored virtual environment was recreated with Python 3.14.6 and refreshed to pip 26.1.2, setuptools 83.0.0, and wheel 0.47.0. A clean editable installation selected current compatible packages from the project constraints. Virtual-environment files remain ignored.

Immediately after the clean install, `pip check` passed and the audit fell from 24 records to one pytest advisory. This confirmed that most baseline findings were caused by stale transitive packages in the old environment, but explicit minimum-safe constraints are still required for repeatable clean installations.

## Remediation batches

| Batch | Commit | Result |
|---|---|---|
| Python environment and test tooling | `b1b4a70` | python-dotenv minimum raised to 1.2.2, pytest to the safe 9.x line, and packaging build minimums refreshed; 127 tests passed and Python audit reached zero |
| Document rendering | `8bfcb70` | ReportLab/Pillow safe floors recorded and PDF header, EOF, size, and page-object integrity assertions added; six PDF tests and 127 total tests passed |
| FastAPI runtime | `c5ab2eb` | FastAPI 0.139 and Starlette 1.3.1 recorded as a compatible pair; request, auth, CORS, health, OpenAPI, and all 127 tests passed |
| Frontend tooling | `1c437b6` | Vite 8.1.4, Vitest 4.1.10, and the compatible React plugin installed; npm audit reached zero and all 45 tests, lint, and build passed |
| Bundle splitting | `cea60ce` | Large route pages are loaded on demand; the entry chunk fell from 527.24 kB to 367.94 kB and the chunk-size warning was removed |

No vulnerability was suppressed or ignored. Final Python and npm advisory counts are both zero.

## Exposure classification

- FastAPI, Starlette, ReportLab, Pillow, python-dotenv, and their request/document/configuration paths are production runtime concerns.
- pytest is development and test tooling.
- pip, setuptools, and wheel are environment and packaging tooling.
- Vite, Vitest, esbuild, `@vitest/mocker`, and `vite-node` are frontend build, development-server, and test tooling; they are not separate browser runtime packages.

## Unimplemented review surfaces

BuildIQ currently has no uploaded-image workflow, file-upload API, external background-task queue, or custom file-upload validation layer. Those checks are therefore not claimed. PDF generation, storage metadata, protected download, fonts, pagination behavior, and file integrity are covered by the existing document workflow and focused smoke validation.

## Remaining non-advisory warnings

- Python 3.14 exposes existing `datetime.utcnow()` deprecation warnings in application and SQLAlchemy-driven timestamp paths. These do not represent unresolved dependency advisories, but timezone-aware datetime migration should be handled as separate application work.
- Starlette reports that its compatibility import for `httpx` test clients is deprecated in favor of `httpx2`. The current test client remains functional and all tests pass. Changing test-client libraries is not required to resolve an advisory and should be reviewed separately.
- npm reports a deprecation notice for the transitive `whatwg-encoding` package during installation. `npm audit` reports zero vulnerabilities.

## Final validation

The final CI-equivalent pass uses a clean `npm ci`, backend pytest, `pip check`, `pip-audit --local`, frontend tests, ESLint, production build, `npm audit --audit-level=high`, Markdown link validation, Gitleaks, `git diff --check`, and architecture SVG semantic integrity verification.
