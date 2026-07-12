# Deployment Principles

This public document defines release expectations without exposing environment-specific topology. Private operational runbooks must contain the actual hosts, users, paths, service definitions, certificates, secrets, backup locations, and rollback commands.

## Release inputs

- Reviewed commit and recorded previous revision
- Passing backend and frontend quality gates
- Verified runtime and dependency compatibility
- Private production configuration with generated secrets
- Database migration plan and current backup/restore evidence
- Named deploy and rollback owners

## Release sequence

1. Verify the target environment and current revision through a private runbook.
2. Create and verify the required database and application backups.
3. Fetch the reviewed revision and verify its commit hash.
4. Install locked backend and frontend dependencies.
5. Run backend tests, frontend tests, lint, and production build.
6. Validate production configuration before starting the application.
7. Apply migrations only after the backup gate passes.
8. Switch the release using the environment's approved service manager and reverse proxy.
9. Verify health, authentication, tenant isolation, authorization, core workflows, document generation, and logs.
10. Record the deployed revision and verification evidence.

## Production configuration

Production must fail closed when:

- the signing secret is missing, known, or too short;
- debug mode is enabled;
- allowed origins are empty, wildcarded, or non-HTTPS;
- database credentials use documented development defaults;
- generated-document storage is not absolute and writable;
- environment identity is ambiguous.

Configuration values and topology must not be committed or printed in release reports.

## Database safety

Migrations require a fresh backup, a recorded identifier, a tested restoration procedure, and a rollback owner. Application rollback does not imply database rollback. Destructive or irreversible migrations require a separately approved data plan.

## Verification

At minimum verify:

- application and API health;
- authentication and current-session loading;
- company/tenant separation;
- negative permission checks;
- project, calculation, estimate, payment, and expense workflows;
- PDF generation and protected download;
- production assets and API routing;
- service and application logs;
- clean deployed Git state.

## Rollback

Rollback must restore the previous reviewed application revision, rebuild compatible assets, restart through the approved service manager, and repeat health and core-flow verification. Database restoration is a separate, explicitly approved action.
