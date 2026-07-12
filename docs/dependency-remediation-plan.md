# Dependency Remediation Plan

## Purpose

This plan records the dependency audit observed during GitHub Professionalization 002. It does not change dependency declarations or lockfiles. Versions below are the minimum fixed versions reported by the audit tools on 13 July 2026; compatibility must be confirmed against the current direct dependency ranges before adoption.

## Python production dependencies

| Package | Current version | Audit severity | Safe target | Risk | Affected area | Recommendation |
|---|---:|---|---:|---|---|---|
| Pillow | 11.3.0 | Multiple advisories | 12.2.0 | Medium: major-version update of a ReportLab transitive dependency | PDF/image processing through ReportLab | Upgrade in an isolated branch; regenerate and visually compare representative PDFs |
| Starlette | 0.49.3 | Multiple advisories | 1.3.1 | High: FastAPI controls the compatible Starlette range | HTTP runtime, middleware, requests and responses | Upgrade FastAPI and Starlette as a compatible pair; run the entire API and authorization suite |
| python-dotenv | 1.2.1 | One advisory | 1.2.2 | Low | Environment loading through runtime/tooling dependencies | Accept the patch update after configuration tests pass |

Pillow, Starlette, and python-dotenv are transitive in the current environment rather than directly pinned in `backend/pyproject.toml`. Do not add arbitrary direct pins solely to silence the scanner; first resolve them through compatible versions of ReportLab, FastAPI, or Uvicorn as appropriate.

## Python development and packaging tooling

| Package | Current version | Audit severity | Safe target | Risk | Affected area | Recommendation |
|---|---:|---|---:|---|---|---|
| pytest | 8.4.2 | One advisory | 9.0.3 | Medium: major-version test-runner update | Test tooling only | Upgrade after production dependencies; resolve plugin/API changes and rerun all tests |
| pip | 26.0.1 | Multiple advisories | 26.1.2 | Low to medium | Local/CI package installation | Upgrade the environment bootstrap tool before reinstalling dependencies |
| setuptools | 58.0.4 | Multiple advisories | 78.1.1 | Medium: large packaging-tool jump; current project build requirement already requests `>=69` | Build backend and local environment | Recreate the virtual environment with a current setuptools rather than mutating an old environment in place |

The old setuptools version is environment residue: `backend/pyproject.toml` already declares `setuptools>=69.0` for builds. A clean environment should be used to distinguish project constraints from local-tool drift.

## npm build and test dependencies

All reported npm packages are development, test, or build-tool dependencies. They are not application runtime libraries shipped as separate server packages, but vulnerable development servers and test tooling still matter to contributors and CI.

| Package | Current version | Severity | Safe target reported by npm | Risk | Affected area |
|---|---:|---|---:|---|---|
| Vite | 5.4.21 | High | 8.1.4 | High: semver-major with Node/plugin/config compatibility changes | Build system and development server |
| Vitest | 2.1.9 | Critical | 4.1.10 | High: semver-major test-runner update | Unit/component testing |
| esbuild | 0.21.5 | Moderate | Resolved through Vite 8.1.4 | High through parent upgrade | Transitive build compiler/development server |
| `@vitest/mocker` | 2.1.9 | Moderate | Resolved through Vitest 4.1.10 | High through parent upgrade | Transitive test mocking |
| `vite-node` | 2.1.9 | Moderate | Resolved through Vitest 4.1.10 | High through parent upgrade | Transitive test execution |

`npm audit fix --force` must not be used: npm reports that the available remediation changes major versions.

## Recommended upgrade order

1. Create a dedicated dependency-remediation branch and establish clean Python and Node environments.
2. Upgrade pip and recreate the Python virtual environment so the declared setuptools build requirement is honored.
3. Apply the python-dotenv patch and run configuration, authentication, and full backend tests.
4. Upgrade ReportLab/Pillow compatibly; regenerate and visually compare PDFs.
5. Upgrade FastAPI/Starlette compatibly; run API-contract, CORS, authorization, tenant-isolation, and full backend tests.
6. Upgrade Vite and its React plugin together; verify the production build and local development server.
7. Upgrade Vitest and its transitive tooling; update test configuration only where required and rerun all frontend tests.
8. Upgrade pytest last among Python project dependencies, then rerun the complete backend suite.
9. Re-run `pip check`, `pip-audit`, `npm audit`, Gitleaks, and the complete CI matrix before review.

Production dependency remediation should be reviewed before development-only tooling because it affects the deployed request, document, and configuration paths. Each major upgrade should remain independently reviewable; do not combine it with application features.
