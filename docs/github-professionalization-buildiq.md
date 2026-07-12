# GitHub Professionalization Review: BuildIQ

## Executive review

BuildIQ now presents a substantially stronger public engineering story: a concise evidence-led README, an implementation-aware architecture document, real application screenshots, contributor and security guidance, repository templates, dependency automation, and a baseline CI workflow.

The strongest current code lineage is the reviewed `develop` lineage used for this program. The public default branch must not remain a scaffold indefinitely. After this branch is reviewed, the recommended path is a pull request that promotes the approved lineage to `main`, followed by changing no default-branch setting until that merge is complete and verified. This program does not change GitHub settings, visibility, branches, or history.

**Recruiter readiness score: 84/100.** The repository now demonstrates product scope, architecture judgment, security boundaries, deterministic domain logic, and release discipline. The remaining deductions are primarily for default-branch drift, incomplete authorization and financial hardening, absent worker/permission management screens, and unresolved license choice.

## Repository improvements

- Rewrote the README around implemented evidence, active development, and explicitly separate future ideas.
- Added recruiter-quality screenshots from the repository's sanitized local demonstration flow.
- Added Mermaid context and container views, an exported SVG, domain boundaries, and implemented-versus-planned architecture notes.
- Added contributor, security, changelog, ownership, issue, pull-request, and dependency-update files.
- Added CI jobs for backend tests and dependency checks, frontend tests/lint/build/audit, and full-history Gitleaks scanning.
- Replaced environment-specific deployment material with generic deployment principles.

## Security cleanup

The current working tree no longer documents a production domain, host name, IP address, Linux account, SSH command, deployment checkout path, or backup path. Production example environment files now use reserved example domains and generic private-storage placeholders. The environment-specific deployment script and runbook were removed from the proposed public state.

Security review covers current-tree topology searches, Gitleaks, a secondary secret-pattern scan, Python and npm dependency audits, configuration tests, and Git-history reference review. Public Git history may retain earlier operational references even after current-tree cleanup. Rewriting history would invalidate commit identifiers and existing clones, so it requires a separate, explicit owner decision and coordinated credential/topology risk review; it is not performed here.

No existing security gate was weakened. The added CI workflow makes security checks visible but does not substitute for branch-protection configuration.

## README review

The README now includes the requested title, status, executive summary, rationale, capabilities, architecture, stack, security philosophy, screenshots, installation, testing, documentation map, roadmap, license, and disclaimer sections.

Claims are deliberately bounded:

- Implemented, in-development, and future work are separated.
- No unsupported AI capability is claimed.
- No customer, adoption, revenue, or production-success claim is made.
- Worker and permission management screenshots are not fabricated because dedicated frontend surfaces do not currently exist.

## Documentation review

`docs/architecture.md` documents context, containers, domain boundaries, authentication, authorization, subscriptions, background processing, storage, and notifications. It explicitly records that the current release candidate has no external background queue and no external notification subsystem. Mermaid source and an exported SVG are included.

The repository now also includes:

- `SECURITY.md`
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- `.github/CODEOWNERS`
- issue and pull-request templates
- Dependabot configuration
- generic deployment principles

Existing blueprint documents may describe target-state design. The README directs readers to current code and the exported OpenAPI contract for implemented behavior.

## GitHub metadata recommendations

These are recommendations only; no repository setting is changed.

- **Description:** Macedonian-first construction management platform with deterministic calculations, tenant-scoped workflows, estimates, payments, and PDF documents.
- **Homepage:** `https://aleksandardimovski.me/projects/buildiq`
- **Topics:** `construction`, `project-management`, `fastapi`, `react`, `postgresql`, `typescript`, `architecture`, `product-engineering`
- **Suggested tags:** create `v0.9.0-rc1` only after the reviewed branch/default-branch alignment and release-candidate gates are complete; reserve `v1.0.0` for a production-ready milestone.
- **Branch protection:** require pull requests, one approval, CODEOWNERS review, resolved conversations, passing backend/frontend/secrets checks, no force pushes or deletion, linear history, and enforcement for administrators. Signed commits are a useful additional policy if contributors can support it consistently.

## License review

No license file or other owner-approved licensing decision was found. An MIT license must not be inferred merely because the repository is public. The README therefore states that no open-source license is granted and that all rights are reserved.

The owner must explicitly choose between a proprietary/public-source posture and an open-source license. If open source is selected, MIT is a plausible simple permissive option, but adding it requires affirmative approval and a dependency-license compatibility review.

## Remaining risks and cleanup

1. Promote the reviewed strong lineage to `main`; the current public default branch is not the strongest public state.
2. Decide and document the repository license.
3. Complete the route-to-permission matrix and negative authorization coverage.
4. Complete fixed-precision money, immutable state-transition, and wider audit-event work.
5. Add dedicated worker and permission management product surfaces before claiming or screenshotting them.
6. Improve the mobile navigation presentation; it reflows without content clipping but remains visually long.
7. Decide whether historical topology references warrant a coordinated history rewrite. Do not rewrite history casually.
8. Require the new CI checks through branch protection after the workflow is reviewed on GitHub.
9. Dependency advisories identified by this review were resolved in Program 003. Continue enforcing `pip-audit` and `npm audit --audit-level=high` in CI and review future major upgrades separately.

## Validation interpretation

BuildIQ is a Python/FastAPI and React/TypeScript repository. Composer validation, `php artisan test`, and Pint are not applicable because the repository has no Composer manifest, Artisan entry point, or PHP source. Equivalent repository-native validation is backend pytest and dependency checks plus frontend test, lint, build, and npm audit.

All final command outcomes are recorded in the program handoff rather than hard-coded here, so this document does not become misleading when dependencies or tests change.
