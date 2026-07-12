# Dependency Upgrade Compatibility

## Supported toolchain

- Python: 3.12 or newer, with CI validating Python 3.12.
- Node.js: 20.19+ or 22.12+.
- npm: the npm release provided by the selected supported Node line.

Vite 8 requires Node 20.19+ or 22.12+. Vitest 4 requires Node 20+ and Vite 6+, so the selected Vite 8.1.4, Vitest 4.1.10, and React plugin 6.x combination is within the published compatibility boundaries.

Primary migration references:

- [Vite 8 announcement and Node requirements](https://vite.dev/blog/announcing-vite8)
- [Vite 8 migration guide](https://vite.dev/guide/migration)
- [Vitest 4 migration guide](https://vitest.dev/guide/migration)
- [FastAPI package and dependency information](https://pypi.org/project/fastapi/)
- [Starlette 1.3.1 package provenance](https://pypi.org/project/starlette/)

## Python compatibility review

FastAPI 0.139.0 installed Starlette 1.3.1 from its declared compatible dependency range in a fresh environment. The pair was then made explicit in project metadata to prevent a future clean install from selecting the vulnerable Starlette line. Request validation, response serialization, middleware/CORS, authentication dependencies, exception behavior, health, production startup gates, and OpenAPI export were exercised.

No application file-upload routes, background tasks, or lifespan handlers exist, so no compatibility claim is made for those unimplemented surfaces. TestClient remains functional, although Starlette warns that its `httpx` compatibility import is deprecated in favor of `httpx2`; that is a future test-tool migration, not a current security advisory.

python-dotenv 1.2.2 preserves the Pydantic Settings integration used by BuildIQ. Existing tests verify production aliases, comma-separated and JSON CORS values, unsafe production defaults, and default loading. The application does not log parsed environment values.

ReportLab 4.5.1 and Pillow 12.3.0 preserve the implemented PDF workflow. BuildIQ generates PDFs from server-owned estimate data and does not accept uploaded images. Integrity assertions and authorization/scoping tests protect the actual path in use.

## Frontend compatibility review

Vite 8 replaces the prior Rollup/esbuild build pipeline with Rolldown/Oxc-based tooling. BuildIQ used no custom Rollup options, esbuild optimizer settings, Sass legacy API, aliases, or advanced plugin hooks, so `vite.config.ts` required no migration change. Environment variables still use Vite's `VITE_` convention, and production output remains under `dist/` with hashed assets.

Vitest 4 removed or changed several advanced coverage, reporter, and module-runner APIs. BuildIQ uses none of the removed options: it defines jsdom, globals, and one setup file. All 45 tests passed after the upgrade, including API mocks and authentication/cache behavior.

The React plugin was upgraded with Vite because its peer range requires Vite 8. No unrelated React, router, query, form, validation, or UI dependency was upgraded intentionally.

## Bundle compatibility

The large entry was caused primarily by statically importing every product page, including Projects, Estimates, Customers, Calculations, Expenses, and Payments. Route-level `React.lazy` loading now emits separate route chunks. Login stays eagerly loaded to preserve immediate authentication rendering and synchronous test expectations.

User-visible behavior is limited to a short accessible Macedonian loading state while a protected route chunk is fetched. The entry chunk is 367.94 kB (112.83 kB gzip), and the previous 500 kB warning is gone.

## Reproducibility

Frontend dependencies are locked by `frontend/package-lock.json` and installed with `npm ci`. Python direct dependencies use bounded compatible ranges in `backend/pyproject.toml`; CI uses Python 3.12, installs the project and audit tool in a clean hosted environment, then runs `pip check`, `pip-audit --local`, and pytest. Python does not yet have a fully hashed transitive lockfile, which remains a reproducibility improvement rather than an unresolved advisory.
