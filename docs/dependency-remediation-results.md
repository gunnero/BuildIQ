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

Batch results and commit hashes are appended after each independently validated change. No advisory is suppressed or ignored.

## Exposure classification

- FastAPI, Starlette, ReportLab, Pillow, python-dotenv, and their request/document/configuration paths are production runtime concerns.
- pytest is development and test tooling.
- pip, setuptools, and wheel are environment and packaging tooling.
- Vite, Vitest, esbuild, `@vitest/mocker`, and `vite-node` are frontend build, development-server, and test tooling; they are not separate browser runtime packages.

## Unimplemented review surfaces

BuildIQ currently has no uploaded-image workflow, file-upload API, external background-task queue, or custom file-upload validation layer. Those checks are therefore not claimed. PDF generation, storage metadata, protected download, fonts, pagination behavior, and file integrity are covered by the existing document workflow and focused smoke validation.
