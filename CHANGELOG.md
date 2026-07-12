# Changelog

All notable public changes to BuildIQ are recorded here. The project is in release-candidate development and does not yet promise semantic-versioning compatibility.

## Unreleased

### Dependency remediation

- Resolved the reviewed Python and frontend dependency advisories without audit exclusions or forced upgrades.
- Upgraded the FastAPI/Starlette, ReportLab/Pillow, pytest, Vite, Vitest, and related toolchain within tested compatibility boundaries.
- Added route-level code splitting, reducing the primary JavaScript entry from approximately 520 kB to 367.94 kB.
- Expanded CI with Python auditing and repository documentation/configuration validation.

### Added

- Flagship repository presentation and explicit implementation-status boundaries
- Public architecture documentation and exported diagram
- Security and contribution policies
- GitHub issue, pull request, ownership, dependency-update, and CI foundations
- Sanitized recruiter-oriented product screenshots

### Security

- Removed environment-specific deployment topology from the current public tree
- Added history-aware secret scanning to the repository quality gate

## 0.9.0-rc1

- Added the end-to-end customer, property, project, room, measurement, painting calculation, estimate, PDF, payment, and expense demonstration flow.
- Added company scoping, subscription foundations, role and permission models, production configuration gates, and expanded security tests.
- Added backend and frontend test coverage, an exported OpenAPI contract, release-candidate review documentation, and a Macedonian user guide.

Earlier engineering notes remain in [`docs/changelog.md`](docs/changelog.md). This root changelog is authoritative for public release notes going forward.
