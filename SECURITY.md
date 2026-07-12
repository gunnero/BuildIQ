# Security Policy

## Supported versions

BuildIQ is in active release-candidate development. Security fixes are applied only to the latest reviewed branch. No production-support or long-term-support commitment is made.

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability. Email `aleksandar.dimovski@me.com` with:

- affected revision or version;
- clear reproduction steps;
- expected and observed behavior;
- impact and affected data boundary;
- any proof of concept that does not contain real customer or production data.

Do not access data that is not yours, perform denial-of-service testing, publish secrets, or target a live environment. Acknowledgement and remediation timing depend on severity and reproducibility.

## Security model

- All business data is company-scoped.
- Authentication does not imply authorization.
- Permission enforcement belongs to backend route and service boundaries.
- Financial totals, calculations, and document generation are backend-owned.
- Generated documents use private storage and protected downloads.
- Production must reject unsafe secrets, debug mode, origins, database defaults, and storage paths.
- Important history is archived, versioned, or reversed rather than silently deleted.

See [`docs/architecture.md`](docs/architecture.md), [`docs/014-security.md`](docs/014-security.md), and [`docs/035-security-sprint-1.md`](docs/035-security-sprint-1.md).

## Public evidence

Issues, pull requests, screenshots, logs, and fixtures must not contain credentials, customer data, private URLs, internal hosts, IP addresses, production topology, database dumps, or operational backups. Use synthetic local data and placeholder configuration for reproductions.
