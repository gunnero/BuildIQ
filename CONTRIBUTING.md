# Contributing

BuildIQ is publicly reviewable but is not currently an open contribution project. Unsolicited pull requests may be closed. Discuss a proposed change in an issue before investing significant work.

## Development principles

- Preserve Macedonian user-facing language and English code/API identifiers.
- Keep authoritative calculations, totals, permissions, and state transitions in the backend.
- Scope every company-owned read and write on the server.
- Do not add direct AI-provider SDKs or unsupported AI claims.
- Do not add production infrastructure, credentials, private data, or confidential strategy.
- Keep changes narrow, reviewed, tested, and reversible.

## Local quality gate

```bash
(cd backend && ../.venv/bin/pytest)
(cd frontend && npm ci)
(cd frontend && npm test -- --run)
(cd frontend && npm run lint)
(cd frontend && npm run build)
git diff --check
```

Run dependency and secret checks appropriate to the changed surface. Add negative authorization and tenant-isolation tests for security-sensitive changes.

## Pull requests

- Branch from the current reviewed integration branch.
- Explain the problem, architecture impact, security impact, and validation evidence.
- Keep unrelated formatting or generated output out of the patch.
- Update documentation and the changelog when public behavior changes.
- Never weaken an existing security test or release gate to make CI pass.

By submitting a contribution, you confirm that you have the right to submit it. Acceptance does not change the repository's all-rights-reserved license status without an explicit written license decision.
